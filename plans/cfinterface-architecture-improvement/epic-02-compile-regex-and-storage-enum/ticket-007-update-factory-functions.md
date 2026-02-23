# ticket-007 Update All Factory Functions to Accept StorageType Enum

## Context

### Background

cfinterface has 4 `factory()` functions that dispatch between Textual and Binary repository implementations based on a `kind: str` parameter. After ticket-006 introduced the `StorageType` enum, these factory functions need to accept both `str` and `StorageType` as input for backward compatibility.

### Relation to Epic

This is the third ticket in Epic 02. It bridges the gap between the new enum (ticket-006) and the existing factory dispatch pattern. After this ticket, factory functions work with both old string API and new enum API.

### Current State

The 4 factory functions share an identical pattern:

```python
def factory(kind: str) -> Type[Repository]:
    mappings: Dict[str, Type[Repository]] = {
        "TEXT": TextualRepository,
        "BINARY": BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
```

Located in:

1. `cfinterface/adapters/components/repository.py` line 250
2. `cfinterface/adapters/components/line/repository.py` line 184
3. `cfinterface/adapters/reading/repository.py` line 124
4. `cfinterface/adapters/writing/repository.py` line 104

All 4 use `Dict[str, Type[Repository]]` with keys `"TEXT"` and `"BINARY"`, and default to `TextualRepository` when the key is not found.

## Specification

### Requirements

1. Update the `kind` parameter type hint from `str` to `Union[str, StorageType]` in all 4 factory functions
2. Update the mapping dict keys to use `StorageType` enum members
3. When `kind` is a plain `str`, convert it to `StorageType` before lookup (if it matches a valid value)
4. Preserve the fallback behavior: unknown values default to `TextualRepository`
5. Since `StorageType(str, Enum)` compares equal to its string value, the dict lookup works with both str and StorageType keys natively when using `StorageType` as keys

### Inputs/Props

- `kind: Union[str, StorageType]` -- the storage type, either as a string or enum member

### Outputs/Behavior

- `factory("TEXT")` returns `TextualRepository` (backward compat)
- `factory("BINARY")` returns `BinaryRepository` (backward compat)
- `factory(StorageType.TEXT)` returns `TextualRepository` (new)
- `factory(StorageType.BINARY)` returns `BinaryRepository` (new)
- `factory("")` returns `TextualRepository` (existing fallback behavior)
- `factory("INVALID")` returns `TextualRepository` (existing fallback behavior)

### Error Handling

No errors raised -- the fallback behavior is preserved for unrecognized values.

## Acceptance Criteria

- [ ] Given `factory(StorageType.TEXT)`, when called in each of the 4 modules, then it returns the respective `TextualRepository` class
- [ ] Given `factory(StorageType.BINARY)`, when called in each of the 4 modules, then it returns the respective `BinaryRepository` class
- [ ] Given `factory("TEXT")`, when called in each of the 4 modules, then it still returns `TextualRepository` (backward compat)
- [ ] Given `factory("BINARY")`, when called in each of the 4 modules, then it still returns `BinaryRepository` (backward compat)
- [ ] Given `factory("")`, when called, then it returns `TextualRepository` (existing default behavior)
- [ ] Given all 4 factory function signatures, when inspected, then the `kind` parameter accepts `Union[str, StorageType]`
- [ ] Given the full test suite, when `pytest tests/` is run, then all existing tests pass

## Implementation Guide

### Suggested Approach

Since `StorageType` extends `str`, and `StorageType.TEXT == "TEXT"` is `True`, the simplest approach is to use `StorageType` members as dict keys. Because of the `str` mixin, lookups with plain strings will also match:

For each of the 4 factory functions, update them to:

```python
from cfinterface.storage import StorageType

def factory(kind: Union[str, "StorageType"]) -> Type[Repository]:
    mappings: Dict[str, Type[Repository]] = {
        StorageType.TEXT: TextualRepository,
        StorageType.BINARY: BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
```

This works because:

- `mappings[StorageType.TEXT]` works directly (enum key lookup)
- `mappings["TEXT"]` also works because `StorageType.TEXT == "TEXT"` and dict uses `__eq__` + `__hash__` for lookup. Since `StorageType(str, Enum)` inherits `str.__hash__`, `hash(StorageType.TEXT) == hash("TEXT")`.

**Important**: Use a string annotation `"StorageType"` to avoid circular imports in adapter modules that don't already import from cfinterface.storage. Alternatively, import at module level since `cfinterface/storage.py` has no dependencies on adapter modules.

### Key Files to Modify

1. `cfinterface/adapters/components/repository.py` -- lines 250-255
2. `cfinterface/adapters/components/line/repository.py` -- lines 184-189
3. `cfinterface/adapters/reading/repository.py` -- lines 124-129
4. `cfinterface/adapters/writing/repository.py` -- lines 104-109

### Patterns to Follow

- Import `StorageType` at the top of each module
- Use `Union[str, StorageType]` for the parameter type hint (not just `StorageType`, to preserve backward compat)
- Keep `TextualRepository` as the default fallback

### Pitfalls to Avoid

- Do NOT remove the string-based lookup support -- 254+ downstream file types use `STORAGE = "TEXT"` as class attributes
- Do NOT change the return type of the factory functions
- The `Union` type hint import may already exist in some files; check before adding duplicates
- Be careful with the import path: `from cfinterface.storage import StorageType` -- verify there are no circular imports since adapters are imported by components which are imported by the storage module's parent package

## Testing Requirements

### Unit Tests

Add tests to verify enum-based factory dispatch. Create or extend `tests/adapters/components/test_factory.py`:

```python
from cfinterface.storage import StorageType
from cfinterface.adapters.components.repository import (
    factory as component_factory,
    TextualRepository as ComponentTextual,
    BinaryRepository as ComponentBinary,
)
from cfinterface.adapters.components.line.repository import (
    factory as line_factory,
    TextualRepository as LineTextual,
    BinaryRepository as LineBinary,
)
from cfinterface.adapters.reading.repository import (
    factory as reading_factory,
    TextualRepository as ReadingTextual,
    BinaryRepository as ReadingBinary,
)
from cfinterface.adapters.writing.repository import (
    factory as writing_factory,
    TextualRepository as WritingTextual,
    BinaryRepository as WritingBinary,
)


def test_component_factory_with_enum():
    assert component_factory(StorageType.TEXT) is ComponentTextual
    assert component_factory(StorageType.BINARY) is ComponentBinary


def test_component_factory_with_string():
    assert component_factory("TEXT") is ComponentTextual
    assert component_factory("BINARY") is ComponentBinary


def test_line_factory_with_enum():
    assert line_factory(StorageType.TEXT) is LineTextual
    assert line_factory(StorageType.BINARY) is LineBinary


def test_reading_factory_with_enum():
    assert reading_factory(StorageType.TEXT) is ReadingTextual
    assert reading_factory(StorageType.BINARY) is ReadingBinary


def test_writing_factory_with_enum():
    assert writing_factory(StorageType.TEXT) is WritingTextual
    assert writing_factory(StorageType.BINARY) is WritingBinary


def test_factory_default_fallback():
    assert component_factory("") is ComponentTextual
    assert component_factory("INVALID") is ComponentTextual
```

### Integration Tests

Run `pytest tests/` to verify all existing tests pass.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-006
- **Blocks**: ticket-008, ticket-009

## Effort Estimate

**Points**: 2
**Confidence**: High
