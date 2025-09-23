# Deep Analysis: CFInterface Evolution Strategy

## Current Implementation Analysis

After examining the cfinterface core and its real-world applications (`inewave`, `idecomp`, `idessem`), I've identified critical architectural patterns that must be addressed for the performance improvements to be effective.

### The Core Problem: Leaky Abstractions

The current implementation suffers from what I call **"abstraction leakage"** - users have direct access to low-level file operations through the exposed filepointer, leading to:

1. **Unpredictable I/O patterns** that defeat optimization attempts
2. **Mixed responsibility** between framework and user code
3. **Performance bottlenecks** in user-implemented `read()` methods
4. **Incompatibility** with advanced features like memory-mapping

### Real-World Usage Patterns

Analyzing the three repositories reveals common patterns:

#### Pattern 1: Complex State Management in Blocks

```python
# From inewave: BlocoVazoes
def read(self, file: IO, *args, **kwargs) -> Optional["BlocoVazoes"]:
    linha = file.readline()
    campos = linha.split(";")
    # Complex parsing logic with multiple readline() calls
    while True:
        linha = file.readline()
        if BlocoCortes.matches(linha):
            file.seek(file.tell() - len(linha))
            break
        # More parsing...
```

This pattern shows:

- Direct `readline()` calls bypassing the repository abstraction
- Manual seek operations for lookahead parsing
- State management across multiple lines

#### Pattern 2: Dynamic Register Creation

```python
# From idecomp: creates registers on-the-fly
registro = RegistroUT()
registro.data = [...]  # Dynamically populated
self.data.append(registro)
```

#### Pattern 3: Conditional Block Reading

```python
# Context-dependent parsing
if self.versao >= 28:
    # Different parsing logic
    campos = linha.split()
else:
    # Legacy parsing
```

## Proposed Solution: Three-Layer Architecture

### Layer 1: Parser Primitives (Low-Level)

Create a new set of parsing primitives that encapsulate all I/O operations while maintaining flexibility:

```python
from typing import Optional, Protocol, TypeVar, Generic, List
from dataclasses import dataclass
import mmap
import re

T = TypeVar('T')

class ParseContext:
    """Immutable parsing context for functional-style parsing"""
    __slots__ = ['buffer', 'position', 'metadata']

    def __init__(self, buffer: memoryview, position: int = 0, metadata: dict = None):
        self.buffer = buffer
        self.position = position
        self.metadata = metadata or {}

    def advance(self, n: int) -> 'ParseContext':
        """Return new context with advanced position"""
        return ParseContext(self.buffer, self.position + n, self.metadata)

    def peek(self, n: int) -> bytes:
        """Look ahead without advancing"""
        return bytes(self.buffer[self.position:self.position + n])

    def consume(self, n: int) -> tuple[bytes, 'ParseContext']:
        """Consume bytes and return new context"""
        data = bytes(self.buffer[self.position:self.position + n])
        return data, self.advance(n)

    def consume_line(self) -> tuple[str, 'ParseContext']:
        """Consume until newline, return decoded string and new context"""
        end = self.position
        while end < len(self.buffer) and self.buffer[end] != ord('\n'):
            end += 1

        line = bytes(self.buffer[self.position:end]).decode('utf-8')
        # Skip the newline character
        return line, ParseContext(self.buffer, end + 1, self.metadata)

    def mark(self) -> 'ParseMarker':
        """Create a marker for backtracking"""
        return ParseMarker(self.position)

    def restore(self, marker: 'ParseMarker') -> 'ParseContext':
        """Restore to a previous position"""
        return ParseContext(self.buffer, marker.position, self.metadata)

@dataclass
class ParseMarker:
    position: int

class Parser(Protocol[T]):
    """Parser combinator protocol"""
    def parse(self, ctx: ParseContext) -> Optional[tuple[T, ParseContext]]:
        ...

class LineParser(Generic[T]):
    """Parser for line-based formats"""
    def __init__(self, transform_fn):
        self.transform = transform_fn

    def parse(self, ctx: ParseContext) -> Optional[tuple[T, ParseContext]]:
        line, new_ctx = ctx.consume_line()
        result = self.transform(line)
        if result is not None:
            return result, new_ctx
        return None

class SequenceParser(Generic[T]):
    """Parse a sequence of items"""
    def __init__(self, item_parser: Parser[T], min_count: int = 0, max_count: Optional[int] = None):
        self.item_parser = item_parser
        self.min_count = min_count
        self.max_count = max_count

    def parse(self, ctx: ParseContext) -> Optional[tuple[List[T], ParseContext]]:
        results = []
        current_ctx = ctx

        while True:
            if self.max_count and len(results) >= self.max_count:
                break

            result = self.item_parser.parse(current_ctx)
            if result is None:
                break

            item, current_ctx = result
            results.append(item)

        if len(results) >= self.min_count:
            return results, current_ctx
        return None

class LookaheadParser(Generic[T]):
    """Parser with lookahead capability"""
    def __init__(self, parser: Parser[T], lookahead_pattern: re.Pattern):
        self.parser = parser
        self.pattern = lookahead_pattern

    def parse(self, ctx: ParseContext) -> Optional[tuple[T, ParseContext]]:
        marker = ctx.mark()

        # Try to parse
        result = self.parser.parse(ctx)
        if result is None:
            return None

        value, new_ctx = result

        # Check lookahead
        next_line, _ = new_ctx.consume_line()
        if self.pattern.match(next_line):
            # Restore position before lookahead
            return value, ctx.restore(marker).advance(len(next_line))

        return result
```

### Layer 2: Declarative Block Definition

Replace the current imperative `read()` methods with declarative parsing rules:

```python
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import re

class ParseStrategy(Enum):
    SINGLE_LINE = "single_line"
    MULTI_LINE = "multi_line"
    DELIMITED = "delimited"
    FIXED_COUNT = "fixed_count"
    UNTIL_PATTERN = "until_pattern"

@dataclass
class FieldMapping:
    """Maps parsed data to block fields"""
    source: str  # Source field in parsed data
    target: str  # Target attribute name
    transform: Optional[Callable] = None  # Optional transformation

@dataclass
class ParseRule:
    """Declarative parsing rule"""
    strategy: ParseStrategy
    pattern: Optional[re.Pattern] = None
    delimiter: Optional[str] = None
    count: Optional[int] = None
    end_pattern: Optional[re.Pattern] = None
    field_mappings: List[FieldMapping] = field()
    nested_blocks: Optional[List[type]] = None

class DeclarativeBlock(Block):
    """Block with declarative parsing rules"""

    # Class-level parsing rules
    PARSE_RULES: List[ParseRule] = []

    @classmethod
    def parse_with_rules(cls, ctx: ParseContext) -> Optional[tuple['DeclarativeBlock', ParseContext]]:
        """Parse using declarative rules"""
        instance = cls()
        current_ctx = ctx

        for rule in cls.PARSE_RULES:
            result = cls._apply_rule(rule, current_ctx)
            if result is None:
                return None

            data, current_ctx = result
            cls._map_fields(instance, data, rule.field_mappings)

            if rule.nested_blocks:
                nested_result = cls._parse_nested(rule.nested_blocks, current_ctx)
                if nested_result:
                    nested_data, current_ctx = nested_result
                    instance.nested = nested_data

        return instance, current_ctx

    @staticmethod
    def _apply_rule(rule: ParseRule, ctx: ParseContext) -> Optional[tuple[Dict, ParseContext]]:
        """Apply a single parsing rule"""
        if rule.strategy == ParseStrategy.SINGLE_LINE:
            line, new_ctx = ctx.consume_line()
            if rule.delimiter:
                parts = line.split(rule.delimiter)
                return {"parts": parts}, new_ctx
            return {"line": line}, new_ctx

        elif rule.strategy == ParseStrategy.UNTIL_PATTERN:
            lines = []
            current_ctx = ctx

            while True:
                line, next_ctx = current_ctx.consume_line()
                if rule.end_pattern and rule.end_pattern.match(line):
                    # Don't consume the end pattern line
                    break
                lines.append(line)
                current_ctx = next_ctx

            return {"lines": lines}, current_ctx

        elif rule.strategy == ParseStrategy.FIXED_COUNT:
            lines = []
            current_ctx = ctx

            for _ in range(rule.count or 0):
                line, current_ctx = current_ctx.consume_line()
                lines.append(line)

            return {"lines": lines}, current_ctx

        # Add more strategies as needed
        return None

# Example usage matching inewave's BlocoVazoes pattern
class BlocoVazoesDeclarative(DeclarativeBlock):
    BEGIN_PATTERN = re.compile(r"^\s*VAZOES NATURAIS\s*")

    PARSE_RULES = [
        ParseRule(
            strategy=ParseStrategy.SINGLE_LINE,
            delimiter=";",
            field_mappings=[
                FieldMapping("parts", "headers", lambda p: [h.strip() for h in p])
            ]
        ),
        ParseRule(
            strategy=ParseStrategy.UNTIL_PATTERN,
            end_pattern=re.compile(r"^\s*CORTES\s*"),
            field_mappings=[
                FieldMapping("lines", "vazoes_data", lambda lines: [
                    [float(v) for v in line.split()] for line in lines
                ])
            ]
        )
    ]
```

### Layer 3: High-Performance Backends

Implement swappable backends for different performance characteristics:

```python
from abc import ABC, abstractmethod
from typing import Optional, Iterator, BinaryIO
import mmap
import asyncio
import aiofiles

class Backend(ABC):
    """Abstract backend for file operations"""

    @abstractmethod
    def open(self, path: str) -> 'ParseContext':
        """Open file and return initial parse context"""
        pass

    @abstractmethod
    def close(self):
        """Clean up resources"""
        pass

class MMapBackend(Backend):
    """Memory-mapped file backend for large files"""

    def __init__(self, copy_on_write: bool = True):
        self.copy_on_write = copy_on_write
        self.file = None
        self.mmap_obj = None

    def open(self, path: str) -> ParseContext:
        self.file = open(path, 'rb')

        # Use copy-on-write for read-only access
        access = mmap.ACCESS_COPY if self.copy_on_write else mmap.ACCESS_READ

        self.mmap_obj = mmap.mmap(self.file.fileno(), 0, access=access)
        buffer = memoryview(self.mmap_obj)

        return ParseContext(buffer)

    def close(self):
        if self.mmap_obj:
            self.mmap_obj.close()
        if self.file:
            self.file.close()

class StreamingBackend(Backend):
    """Streaming backend for sequential access"""

    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        self.chunks: List[bytes] = []
        self.current_chunk = 0

    def open(self, path: str) -> ParseContext:
        # Pre-load first chunk
        with open(path, 'rb') as f:
            first_chunk = f.read(self.chunk_size)
            self.chunks.append(first_chunk)

        return ParseContext(memoryview(first_chunk))

    def load_chunk(self, index: int) -> Optional[bytes]:
        """Load chunk on demand"""
        # Implementation for lazy loading
        pass

class AsyncBackend(Backend):
    """Asynchronous I/O backend"""

    async def open_async(self, path: str) -> ParseContext:
        async with aiofiles.open(path, 'rb') as f:
            content = await f.read()
            return ParseContext(memoryview(content))

class HybridBackend(Backend):
    """Intelligent backend selection based on file characteristics"""

    def __init__(self, size_threshold: int = 10 * 1024 * 1024):  # 10MB
        self.size_threshold = size_threshold
        self.active_backend = None

    def open(self, path: str) -> ParseContext:
        import os
        file_size = os.path.getsize(path)

        if file_size > self.size_threshold:
            self.active_backend = MMapBackend()
        else:
            self.active_backend = StreamingBackend()

        return self.active_backend.open(path)

    def close(self):
        if self.active_backend:
            self.active_backend.close()
```

## Migration Strategy for Existing Code

### Phase 1: Compatibility Layer (Immediate)

Create a compatibility layer that wraps existing user code:

```python
from typing import IO, Optional
from io import BytesIO, StringIO

class LegacyFileWrapper:
    """Wraps ParseContext to provide file-like interface for legacy code"""

    def __init__(self, ctx: ParseContext):
        self.ctx = ctx
        self._line_cache = []

    def readline(self) -> str:
        """Emulate readline() for legacy code"""
        if self._line_cache:
            return self._line_cache.pop(0)

        line, self.ctx = self.ctx.consume_line()
        return line + '\n'  # Add newline for compatibility

    def read(self, n: int = -1) -> bytes:
        """Emulate read() for legacy code"""
        if n == -1:
            # Read all remaining
            data = bytes(self.ctx.buffer[self.ctx.position:])
            self.ctx = self.ctx.advance(len(data))
            return data

        data, self.ctx = self.ctx.consume(n)
        return data

    def seek(self, offset: int, whence: int = 0):
        """Emulate seek() for legacy code"""
        if whence == 0:  # SEEK_SET
            self.ctx = ParseContext(self.ctx.buffer, offset, self.ctx.metadata)
        elif whence == 1:  # SEEK_CUR
            self.ctx = self.ctx.advance(offset)
        elif whence == 2:  # SEEK_END
            self.ctx = ParseContext(self.ctx.buffer, len(self.ctx.buffer) + offset)

    def tell(self) -> int:
        """Emulate tell() for legacy code"""
        return self.ctx.position

class LegacyBlock(Block):
    """Adapter for legacy block implementations"""

    def __init__(self, legacy_block_class):
        self.legacy_class = legacy_block_class
        self.backend = HybridBackend()

    def read_with_backend(self, path: str) -> Optional[Block]:
        """Read using new backend but legacy parsing logic"""
        ctx = self.backend.open(path)
        wrapper = LegacyFileWrapper(ctx)

        # Call legacy read method
        legacy_instance = self.legacy_class()
        result = legacy_instance.read(wrapper)

        self.backend.close()
        return result
```

### Phase 2: Gradual Migration Tools

Provide tools to help users migrate their code:

```python
import ast
import inspect
from typing import List, Dict, Any

class CodeAnalyzer:
    """Analyze user code for migration opportunities"""

    def analyze_block_class(self, block_class: type) -> Dict[str, Any]:
        """Analyze a block class for migration patterns"""
        source = inspect.getsource(block_class.read)
        tree = ast.parse(source)

        analysis = {
            'io_operations': [],
            'complexity': 0,
            'migration_difficulty': 'low',
            'suggested_strategy': None
        }

        # Find I/O operations
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['readline', 'read', 'seek', 'tell']:
                        analysis['io_operations'].append({
                            'operation': node.func.attr,
                            'line': node.lineno
                        })

        # Determine migration strategy
        if len(analysis['io_operations']) < 5:
            analysis['suggested_strategy'] = ParseStrategy.SINGLE_LINE
        elif any(op['operation'] == 'seek' for op in analysis['io_operations']):
            analysis['suggested_strategy'] = ParseStrategy.UNTIL_PATTERN
            analysis['migration_difficulty'] = 'medium'
        else:
            analysis['suggested_strategy'] = ParseStrategy.MULTI_LINE

        return analysis

class MigrationGenerator:
    """Generate migration code from analysis"""

    def generate_declarative_block(self, block_class: type, analysis: Dict) -> str:
        """Generate declarative block code from legacy block"""

        template = '''
class {name}Declarative(DeclarativeBlock):
    BEGIN_PATTERN = {pattern}

    PARSE_RULES = [
        ParseRule(
            strategy=ParseStrategy.{strategy},
            # TODO: Add field mappings based on your logic
            field_mappings=[
                # FieldMapping("source", "target", transform_function)
            ]
        )
    ]
'''

        return template.format(
            name=block_class.__name__,
            pattern=block_class.BEGIN_PATTERN,
            strategy=analysis['suggested_strategy'].name
        )
```

## Performance Optimization Strategies

### 1. Zero-Copy Operations

Implement zero-copy operations throughout the stack:

```python
import numpy as np
from typing import List, Tuple

class ZeroCopyField:
    """Field that operates directly on memory views"""

    def __init__(self, dtype: np.dtype, offset: int, shape: Tuple[int, ...] = None):
        self.dtype = dtype
        self.offset = offset
        self.shape = shape or (1,)

    def read(self, buffer: memoryview) -> np.ndarray:
        """Read field as numpy array without copying"""
        # Create array view directly from buffer
        arr = np.frombuffer(buffer, dtype=self.dtype, offset=self.offset)

        if self.shape != (1,):
            arr = arr.reshape(self.shape)

        return arr

    def write(self, buffer: memoryview, value: np.ndarray):
        """Write directly to buffer without copying"""
        # Get mutable view
        arr = np.frombuffer(buffer, dtype=self.dtype, offset=self.offset)
        arr[:] = value.flat

class ZeroCopyRegister:
    """Register using zero-copy fields"""

    def __init__(self, fields: List[ZeroCopyField]):
        self.fields = fields
        self._buffer = None

    def bind(self, buffer: memoryview):
        """Bind to a memory buffer"""
        self._buffer = buffer

    def __getattr__(self, name: str):
        """Dynamic attribute access to fields"""
        if name in self.field_map:
            field = self.field_map[name]
            return field.read(self._buffer)
        raise AttributeError(f"No field named {name}")
```

### 2. JIT Compilation for Hot Paths

Use Numba for performance-critical sections:

```python
import numba
from numba import njit, prange
import numpy as np

@njit(parallel=True, cache=True)
def parse_fixed_width_fields(buffer: np.ndarray, field_specs: np.ndarray) -> np.ndarray:
    """
    JIT-compiled parser for fixed-width fields

    field_specs: array of (start, end, type) tuples
    """
    n_lines = buffer.shape[0]
    n_fields = field_specs.shape[0]

    results = np.empty((n_lines, n_fields), dtype=np.float64)

    for i in prange(n_lines):
        for j in range(n_fields):
            start = field_specs[j, 0]
            end = field_specs[j, 1]

            # Parse based on type
            field_bytes = buffer[i, start:end]
            results[i, j] = parse_number(field_bytes)

    return results

@njit(cache=True)
def parse_number(bytes_data: np.ndarray) -> float:
    """Fast number parsing"""
    result = 0.0
    sign = 1.0
    decimal_places = 0
    in_decimal = False

    for byte in bytes_data:
        if byte == ord('-'):
            sign = -1.0
        elif byte == ord('.'):
            in_decimal = True
        elif ord('0') <= byte <= ord('9'):
            digit = byte - ord('0')
            if in_decimal:
                decimal_places += 1
                result += digit / (10.0 ** decimal_places)
            else:
                result = result * 10 + digit

    return result * sign
```

### 3. Lazy Evaluation and Caching

Implement lazy evaluation for expensive operations:

```python
from functools import cached_property, lru_cache
from typing import Optional, List

class LazyBlock:
    """Block with lazy evaluation of expensive operations"""

    def __init__(self, ctx: ParseContext):
        self._ctx = ctx
        self._parsed = False

    @cached_property
    def data(self) -> List[Dict]:
        """Parse data only when accessed"""
        return self._parse_data()

    @lru_cache(maxsize=128)
    def get_field(self, name: str) -> Optional[Any]:
        """Cache field access"""
        if name in self.data:
            return self.data[name]
        return None

    def _parse_data(self) -> List[Dict]:
        """Expensive parsing operation"""
        # Only executed once, when data is first accessed
        pass

class LazyBlockFile:
    """File with lazy block loading"""

    def __init__(self, path: str, backend: Backend = None):
        self.path = path
        self.backend = backend or HybridBackend()
        self._block_index = None

    @cached_property
    def block_index(self) -> Dict[str, int]:
        """Build block index on first access"""
        index = {}
        ctx = self.backend.open(self.path)

        while ctx.position < len(ctx.buffer):
            line, next_ctx = ctx.consume_line()

            for block_class in self.BLOCKS:
                if block_class.BEGIN_PATTERN.match(line):
                    index[block_class.__name__] = ctx.position
                    break

            ctx = next_ctx

        return index

    def get_block(self, block_type: str) -> Optional[Block]:
        """Load specific block on demand"""
        if block_type not in self.block_index:
            return None

        ctx = self.backend.open(self.path)
        ctx = ctx.advance(self.block_index[block_type])

        # Parse only the requested block
        return self._parse_block_at(ctx, block_type)
```

## API Design Recommendations

### 1. Fluent Interface for Common Operations

```python
from typing import List, Optional, Callable

class FileQuery:
    """Fluent interface for file operations"""

    def __init__(self, file_class: type):
        self.file_class = file_class
        self.filters = []
        self.transforms = []
        self.backend = None

    def with_backend(self, backend: Backend) -> 'FileQuery':
        """Select backend"""
        self.backend = backend
        return self

    def filter_blocks(self, predicate: Callable[[Block], bool]) -> 'FileQuery':
        """Filter blocks"""
        self.filters.append(predicate)
        return self

    def transform(self, transformer: Callable[[Block], Block]) -> 'FileQuery':
        """Transform blocks"""
        self.transforms.append(transformer)
        return self

    def read(self, path: str) -> List[Block]:
        """Execute query"""
        backend = self.backend or HybridBackend()
        ctx = backend.open(path)

        blocks = self.file_class.parse_all(ctx)

        # Apply filters
        for f in self.filters:
            blocks = [b for b in blocks if f(b)]

        # Apply transforms
        for t in self.transforms:
            blocks = [t(b) for b in blocks]

        backend.close()
        return blocks

# Usage example
result = (FileQuery(MyBlockFile)
    .with_backend(MMapBackend())
    .filter_blocks(lambda b: b.type == "DATA")
    .transform(lambda b: b.normalize())
    .read("data.txt"))
```

### 2. Context Managers for Resource Management

```python
from contextlib import contextmanager
from typing import Iterator

class FileSession:
    """Session for batch operations"""

    def __init__(self, backend: Backend = None):
        self.backend = backend or HybridBackend()
        self.open_files = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for ctx in self.open_files.values():
            self.backend.close()

    def open(self, path: str) -> ParseContext:
        """Open file in session"""
        if path not in self.open_files:
            self.open_files[path] = self.backend.open(path)
        return self.open_files[path]

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Transactional operations"""
        # Save state
        saved_states = {p: ctx.position for p, ctx in self.open_files.items()}

        try:
            yield
        except Exception:
            # Rollback on error
            for path, position in saved_states.items():
                self.open_files[path] = ParseContext(
                    self.open_files[path].buffer,
                    position
                )
            raise

# Usage
with FileSession() as session:
    ctx1 = session.open("file1.txt")
    ctx2 = session.open("file2.txt")

    with session.transaction():
        # Operations that can be rolled back
        block1 = Block1.parse(ctx1)
        block2 = Block2.parse(ctx2)
```

## Implementation Roadmap - Revised

### Sprint 1: Foundation (Weeks 1-2)

1. Implement `ParseContext` and basic primitives
2. Create `Backend` interface with `MMapBackend` and `StreamingBackend`
3. Add `LegacyFileWrapper` for backward compatibility
4. Write comprehensive tests

### Sprint 2: Declarative API (Weeks 3-4)

1. Implement `DeclarativeBlock` with `ParseRule` system
2. Create parser combinators for common patterns
3. Add field mapping system
4. Migrate one simple block from `inewave` as proof of concept

### Sprint 3: Performance Layer (Weeks 5-6)

1. Add zero-copy field operations
2. Implement JIT compilation for hot paths
3. Add lazy evaluation and caching
4. Benchmark against current implementation

### Sprint 4: Migration Tools (Weeks 7-8)

1. Build code analyzer for existing blocks
2. Create migration code generator
3. Write migration guide and documentation
4. Create automated test suite for migrated blocks

### Sprint 5: Advanced Features (Weeks 9-10)

1. Implement async backend
2. Add fluent query API
3. Create session management
4. Add transaction support

### Sprint 6: Real-World Integration (Weeks 11-12)

1. Migrate critical blocks from `inewave`
2. Performance testing with real data
3. Documentation and examples
4. Release candidate

## Conclusion

The proposed architecture addresses the fundamental issues while maintaining backward compatibility. The key innovations are:

1. **Separation of I/O from business logic** through `ParseContext`
2. **Declarative parsing** reducing boilerplate and improving optimization opportunities
3. **Pluggable backends** for different performance characteristics
4. **Zero-copy operations** for maximum efficiency
5. **Progressive migration path** for existing code

This approach will make cfinterface competitive with high-performance parsing libraries while maintaining its excellent declarative API design.
