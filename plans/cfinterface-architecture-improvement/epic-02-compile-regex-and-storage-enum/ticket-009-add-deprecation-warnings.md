# ticket-009 Add Deprecation Warnings for String-Based Storage Parameters

## Context

### Background

After ticket-008 migrated all internal usage to `StorageType`, consumers that pass string values like `"TEXT"` or `"BINARY"` should receive deprecation warnings guiding them to use `StorageType` enum members instead. This provides a clear migration path for the 254+ downstream file types.

### Relation to Epic

This is the final ticket in Epic 02. It completes the StorageType migration by adding deprecation warnings that will guide consumer migration without breaking existing code.

### Current State

After ticket-008, all internal code uses `StorageType` members, but the factory functions and method parameters still accept plain strings via `Union[str, StorageType]`. No warnings are emitted when strings are used.

## Specification

### Requirements

1. Add a utility function `_ensure_storage_type(value: Union[str, StorageType]) -> StorageType` in `cfinterface/storage.py`
2. This function converts string values to `StorageType`, emitting a `DeprecationWarning` when a plain string is passed
3. For empty string `""`, return the value as-is WITHOUT a warning (empty string is the internal default, not something consumers set explicitly)
4. Add the deprecation check at the entry points where consumers provide storage values: the `STORAGE` class attribute validation in file class `__init__` methods
5. Do NOT add warnings to every internal method parameter -- only at the consumer-facing entry points

### Inputs/Props

- `value: Union[str, StorageType]` -- the storage value to validate and convert

### Outputs/Behavior

- If `value` is already a `StorageType`: return it unchanged, no warning
- If `value` is `""`: return it unchanged, no warning
- If `value` is `"TEXT"` or `"BINARY"`: return `StorageType(value)`, emit `DeprecationWarning`
- If `value` is any other string: return it unchanged, no warning (the factory fallback handles it)

### Error Handling

No errors raised. Only `DeprecationWarning` via `warnings.warn()`.

## Acceptance Criteria

- [ ] Given `_ensure_storage_type(StorageType.TEXT)`, when called, then it returns `StorageType.TEXT` without emitting a warning
- [ ] Given `_ensure_storage_type("TEXT")`, when called, then it returns `StorageType.TEXT` AND emits a `DeprecationWarning`
- [ ] Given `_ensure_storage_type("")`, when called, then it returns `""` without emitting a warning
- [ ] Given a file class subclass with `STORAGE = "TEXT"`, when instantiated, then a `DeprecationWarning` is emitted mentioning `StorageType.TEXT`
- [ ] Given a file class subclass with `STORAGE = StorageType.TEXT`, when instantiated, then NO warning is emitted
- [ ] Given the full test suite, when `pytest tests/ -W error::DeprecationWarning` is run with internal tests updated to use `StorageType`, then all tests pass

## Implementation Guide

### Suggested Approach

**Step 1**: Add the utility to `cfinterface/storage.py`:

```python
import warnings
from enum import Enum
from typing import Union


class StorageType(str, Enum):
    TEXT = "TEXT"
    BINARY = "BINARY"


def _ensure_storage_type(
    value: Union[str, "StorageType"],
) -> Union[str, "StorageType"]:
    """Validate and optionally convert a storage value.

    Emits a DeprecationWarning when a plain string is used
    instead of a StorageType enum member.

    :param value: The storage value to check
    :type value: str | StorageType
    :return: The validated storage value
    :rtype: str | StorageType
    """
    if isinstance(value, StorageType):
        return value
    if value == "":
        return value
    if value in ("TEXT", "BINARY"):
        warnings.warn(
            f'Using string "{value}" for storage type is deprecated. '
            f"Use StorageType.{value} instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return StorageType(value)
    return value
```

**Step 2**: Add the deprecation check in the three file class `__init__` methods where `self.__storage = self.__class__.STORAGE` is assigned. For example, in `RegisterFile.__init__()`:

```python
def __init__(self, data=RegisterData(DefaultRegister(data=""))) -> None:
    self.__data = data
    self.__storage = _ensure_storage_type(self.__class__.STORAGE)
    ...
```

Apply similarly to `BlockFile.__init__()` and `SectionFile.__init__()`.

The `stacklevel=3` in the warning ensures the warning points to the consumer's subclass definition, not the internal cfinterface code.

### Key Files to Modify

- `cfinterface/storage.py` (add `_ensure_storage_type`)
- `cfinterface/files/registerfile.py` (add deprecation check in `__init__`)
- `cfinterface/files/blockfile.py` (add deprecation check in `__init__`)
- `cfinterface/files/sectionfile.py` (add deprecation check in `__init__`)

### Patterns to Follow

- Use `warnings.warn(..., DeprecationWarning, stacklevel=N)` -- the standard Python deprecation pattern
- `stacklevel` should point to the consumer's code, not internal cfinterface code
- Keep the warning message actionable: tell the user exactly what to use instead

### Pitfalls to Avoid

- Do NOT emit warnings for the empty string `""` default -- this is an internal sentinel, not a consumer-chosen value
- Do NOT add deprecation checks inside hot loops (like per-line reading) -- only at file class instantiation
- Do NOT make the warning an error -- it should be a `DeprecationWarning` that can be suppressed
- Adjust `stacklevel` carefully -- test with an actual consumer subclass to verify the warning points to the right line

## Testing Requirements

### Unit Tests

Create `tests/test_storage_deprecation.py`:

```python
import warnings
from cfinterface.storage import StorageType, _ensure_storage_type


def test_ensure_storage_type_enum_no_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _ensure_storage_type(StorageType.TEXT)
        assert result is StorageType.TEXT
        assert len(w) == 0


def test_ensure_storage_type_string_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _ensure_storage_type("TEXT")
        assert result is StorageType.TEXT
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "StorageType.TEXT" in str(w[0].message)


def test_ensure_storage_type_empty_string_no_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _ensure_storage_type("")
        assert result == ""
        assert len(w) == 0


def test_ensure_storage_type_binary_string_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _ensure_storage_type("BINARY")
        assert result is StorageType.BINARY
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
```

### Integration Tests

Run `pytest tests/` to verify all existing tests pass. Note: existing tests that use `STORAGE = "TEXT"` (string) will now trigger deprecation warnings. The test suite should be run with `-W default::DeprecationWarning` (not `-W error`) to not break.

Update the internal test mocks/fixtures that set `STORAGE = "TEXT"` to use `StorageType.TEXT` instead, so they serve as examples of the correct pattern.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-008
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: High
