# ticket-018 Separate TextualRepository and BinaryRepository Type Signatures

## Context

### Background

The four adapter repository modules each contain an abstract `Repository` base class plus `TextualRepository` and `BinaryRepository` subclasses. Currently, all method signatures use `Union[str, bytes]` for parameters and return types, even though each concrete subclass only ever processes one type. For example, `TextualRepository.matches(pattern: Union[str, bytes], line: Union[str, bytes]) -> bool` will only ever handle `str` arguments, yet its signature accepts `bytes` too. This forces callers to either ignore the type mismatch or defensively add `isinstance` checks. This ticket tightens the concrete subclass signatures to use the specific type (`str` or `bytes`) while keeping the abstract base class using `Union` for polymorphic dispatch.

### Relation to Epic

This ticket narrows repository types so that ticket-019 (Line class typed dispatch) and ticket-020 (Register/Block/Section typed IO) can rely on precise return types from the repositories they call. It builds on ticket-017's overload pattern by ensuring the entire layer below Line has type-safe signatures.

### Current State

Four repository modules exist, each with `TextualRepository`, `BinaryRepository`, abstract `Repository`, and a `factory()` function:

1. **`cfinterface/adapters/components/repository.py`** -- Pattern matching (`matches`, `begins`, `ends`) + file-level `read`/`write`. The abstract `Repository` uses `Union[str, bytes]`. `BinaryRepository.matches()` has a special case: `str` pattern + `bytes` line (decodes line to UTF-8). The `_pattern_cache` and `_compile()` helper are module-level.

2. **`cfinterface/adapters/components/line/repository.py`** -- Field-level line reading/writing. `TextualRepository.read()` takes `Union[str, bytes]` but only processes `str`. `BinaryRepository.write()` already returns `bytes` explicitly.

3. **`cfinterface/adapters/reading/repository.py`** -- File-level reading (context managers). `BinaryRepository.read()` already returns `bytes`. `TextualRepository.read()` already returns `str`.

4. **`cfinterface/adapters/writing/repository.py`** -- File-level writing (context managers). `TextualRepository.write()` checks `isinstance(data, str)`. `BinaryRepository.write()` checks `isinstance(data, bytes)`.

All four `factory()` functions return `Type[Repository]` and use `Dict[Union[str, StorageType], Type[Repository]]` mappings.

## Specification

### Requirements

1. **Abstract base classes stay polymorphic**: Keep `Union[str, bytes]` in all abstract `Repository` base class method signatures. This preserves the polymorphic contract that `factory()` returns.

2. **Concrete subclass signatures narrowed**: In each of the four modules:
   - `TextualRepository` methods use `str` (not `Union[str, bytes]`) for line/data/pattern parameters and return types.
   - `BinaryRepository` methods use `bytes` (not `Union[str, bytes]`) for line/data parameters and return types.

3. **`BinaryRepository.matches()` special case preserved**: In `cfinterface/adapters/components/repository.py`, `BinaryRepository.matches()` must retain its special behavior of accepting `str` pattern with `bytes` line. Use `@overload` to express this:
   - `matches(pattern: bytes, line: bytes) -> bool`
   - `matches(pattern: str, line: bytes) -> bool`

4. **`factory()` return types**: Add `@overload` on all four `factory()` functions so that:
   - `factory(StorageType.TEXT)` returns `Type[TextualRepository]`
   - `factory(StorageType.BINARY)` returns `Type[BinaryRepository]`
   - The implementation signature remains `factory(kind: Union[str, StorageType]) -> Type[Repository]` for the default fallback.

5. **Remove runtime `isinstance` guards in writing repositories**: In `cfinterface/adapters/writing/repository.py`, `TextualRepository.write()` currently checks `isinstance(data, str)` and `BinaryRepository.write()` checks `isinstance(data, bytes)`. These guards can be removed since the type signature now guarantees the correct type. However, keep them as runtime safety for backward compatibility -- just narrow the parameter type annotation.

6. **No changes to `_pattern_cache` or `_compile()`** -- these are already correct and handle both `str` and `bytes` patterns.

### Inputs/Props

No changes to the inputs accepted at runtime. Only type annotations change on the concrete subclasses.

### Outputs/Behavior

- Runtime behavior is identical to the current implementation.
- mypy can now determine that `TextualRepository.read()` returns `str` and `BinaryRepository.read()` returns `bytes`.
- `factory(StorageType.TEXT)` is typed to return `Type[TextualRepository]` via overload, so callers get precise types.

### Error Handling

- No changes to error handling. The `isinstance` guards in writing repositories are kept for runtime safety.

## Acceptance Criteria

- [ ] Given `cfinterface/adapters/components/repository.py`, when inspected, then `TextualRepository.matches()` signature uses `str` for both pattern and line parameters, and `BinaryRepository.matches()` has overloads for `(bytes, bytes)` and `(str, bytes)`.
- [ ] Given `cfinterface/adapters/components/line/repository.py`, when inspected, then `TextualRepository.read()` takes `line: str` (not `Union`) and returns `List[Any]`, and `TextualRepository.write()` returns `str`.
- [ ] Given `cfinterface/adapters/reading/repository.py`, when inspected, then `TextualRepository.read()` returns `str` and `BinaryRepository.read()` returns `bytes` in their type signatures.
- [ ] Given `cfinterface/adapters/writing/repository.py`, when inspected, then `TextualRepository.write()` takes `data: str` and `BinaryRepository.write()` takes `data: bytes`.
- [ ] Given all four `factory()` functions, when inspected, then each has `@overload` for `StorageType.TEXT` and `StorageType.BINARY` arguments.
- [ ] Given `pytest tests/`, when run, then all 268+ tests pass with no regressions.
- [ ] Given `ruff check cfinterface/adapters/`, when run, then no lint errors are reported.

## Implementation Guide

### Suggested Approach

Work through each of the four repository modules in order. For each module:

**Step 1: Tighten concrete subclass signatures**

For `TextualRepository`, change parameter types from `Union[str, bytes]` to `str`. For `BinaryRepository`, change to `bytes`. Only change annotations, not runtime logic.

**Step 2: Add `@overload` on `factory()`**

```python
from typing import overload

@overload
def factory(kind: Literal["TEXT"]) -> Type[TextualRepository]: ...

@overload
def factory(kind: Literal["BINARY"]) -> Type[BinaryRepository]: ...

def factory(kind: Union[str, "StorageType"]) -> Type[Repository]:
    # existing implementation unchanged
```

Note: Use `typing.Literal` (available since Python 3.8) with string literals `"TEXT"` and `"BINARY"` to also cover the legacy string path, and add overloads for the `StorageType` enum members. Since `StorageType(str, Enum)` means `StorageType.TEXT == "TEXT"`, a `Literal["TEXT"]` overload covers both `StorageType.TEXT` and the plain string `"TEXT"`.

Actually, since `StorageType` extends `str`, the `Literal` approach should work. However, to be explicit and safe, add separate overloads:

```python
@overload
def factory(kind: Literal["TEXT"]) -> Type[TextualRepository]: ...

@overload
def factory(kind: Literal["BINARY"]) -> Type[BinaryRepository]: ...

@overload
def factory(kind: Union[str, "StorageType"]) -> Type[Repository]: ...

def factory(kind: Union[str, "StorageType"]) -> Type[Repository]:
    mappings: Dict[Union[str, StorageType], Type[Repository]] = {
        StorageType.TEXT: TextualRepository,
        StorageType.BINARY: BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
```

**Step 3: Handle the `BinaryRepository.matches()` special case**

In `cfinterface/adapters/components/repository.py`, `BinaryRepository.matches()` accepts `str` pattern + `bytes` line. Add overloads:

```python
@staticmethod
@overload
def matches(pattern: bytes, line: bytes) -> bool: ...

@staticmethod
@overload
def matches(pattern: str, line: bytes) -> bool: ...

@staticmethod
def matches(pattern: Union[str, bytes], line: bytes) -> bool:
    if isinstance(pattern, bytes):
        return _compile(pattern).search(line) is not None
    elif isinstance(pattern, str):
        return _compile(pattern).search(line.decode("utf-8")) is not None
    return False
```

**Step 4: Narrow the line/repository module specifically**

In `cfinterface/adapters/components/line/repository.py`:

- `TextualRepository.read(line: str, delimiter: Optional[str] = None) -> List[Any]`
- `TextualRepository.write(values: List[Any], delimiter: Optional[str] = None) -> str`
- `BinaryRepository.read(line: bytes, delimiter: Optional[bytes] = None) -> List[Any]`
- `BinaryRepository.write(values: List[Any], delimiter: Optional[bytes] = None) -> bytes`

Note: The delimiter type should match the line type for consistency.

### Key Files to Modify

- `cfinterface/adapters/components/repository.py`
- `cfinterface/adapters/components/line/repository.py`
- `cfinterface/adapters/reading/repository.py`
- `cfinterface/adapters/writing/repository.py`

### Patterns to Follow

- Follow the `@overload` + implementation pattern established in ticket-017 for `Field.read()`/`write()`.
- Keep abstract base class signatures broad (`Union[str, bytes]`) -- only narrow concrete subclasses.
- Use `typing.Literal` for the `factory()` overloads.

### Pitfalls to Avoid

- Do NOT narrow the abstract `Repository` base class signatures -- they must stay `Union` because code like `RegisterReading.__read_file()` holds a `Repository` reference and calls methods on it polymorphically.
- Do NOT remove the `isinstance` runtime guards in `BinaryRepository.matches()` -- they are needed because the method genuinely handles two input pattern types.
- Do NOT change the `_pattern_cache` or `_compile()` helper -- they already handle both `str` and `bytes`.
- Do NOT change the `factory()` implementation body -- only add overloads on top.
- Be careful with the `BinaryRepository.read()` in `line/repository.py` -- it currently has `# type: ignore` on `field.read(line)`. This ignore may become unnecessary after ticket-017's overloads are in place, but leave it for now if mypy still complains (the `field.read()` call passes `bytes` which is now a valid overload).

## Testing Requirements

### Unit Tests

- Append tests to `tests/adapters/components/test_factory.py`:
  - Test that `component_factory(StorageType.TEXT)` returns `ComponentTextual` (already exists, just verify no regression).
  - Test that `component_factory(StorageType.BINARY)` returns `ComponentBinary` (already exists).
  - Repeat for all four factory functions.

- Append tests to `tests/adapters/components/test_linerepository.py`:
  - Test that `TextualRepository.read("hello, world!")` returns `List[Any]` with correct values (already exists, verify no regression).
  - Test that `BinaryRepository.read(b"hello, world!")` returns `List[Any]` with correct values.
  - Test that `BinaryRepository.write(["hello,", "world!"])` returns `bytes`.

- Append tests to `tests/adapters/components/test_registerrepository.py`:
  - Test that `TextualRepository.matches("pattern", "line")` works.
  - Test that `BinaryRepository.matches("pattern", b"line")` works (str pattern + bytes line).
  - Test that `BinaryRepository.matches(b"pattern", b"line")` works (bytes pattern + bytes line).

### Integration Tests

- Run the full test suite (`pytest tests/`) to confirm no regressions.

### E2E Tests (if applicable)

- Not applicable.

## Dependencies

- **Blocked By**: ticket-017
- **Blocks**: ticket-019, ticket-020

## Effort Estimate

**Points**: 3
**Confidence**: High
