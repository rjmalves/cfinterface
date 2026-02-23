# ticket-006 Create StorageType Enum Module

## Context

### Background

The string literals `"TEXT"` and `"BINARY"` are used throughout cfinterface as a dispatch mechanism for choosing between textual and binary file handling. These strings are passed as `storage: str` parameters through the entire call stack: File classes -> Reading/Writing classes -> Component repository factories -> Register/Block/Section methods. Using plain strings is error-prone (no IDE completion, no type checking, typos fail silently) and not self-documenting.

### Relation to Epic

This is the second ticket in Epic 02. It creates the `StorageType` enum definition without modifying any existing code. Subsequent tickets (007, 008, 009) will integrate this enum into the codebase.

### Current State

There is no `StorageType` enum anywhere in the codebase. The string `"TEXT"` appears as a default in:

- `Section.STORAGE: str = "TEXT"` (line 12)
- `RegisterFile.STORAGE = "TEXT"` (line 23)
- `BlockFile.STORAGE = "TEXT"` (line 21)
- `SectionFile.STORAGE = "TEXT"` (line 21)

The strings appear in factory function mappings in 4 files:

- `cfinterface/adapters/components/repository.py` lines 251-254
- `cfinterface/adapters/components/line/repository.py` lines 185-188
- `cfinterface/adapters/reading/repository.py` lines 125-128
- `cfinterface/adapters/writing/repository.py` lines 104-108

## Specification

### Requirements

1. Create a new module `cfinterface/storage.py` containing the `StorageType` enum
2. The enum has exactly two members: `TEXT` and `BINARY`
3. The enum values are the strings `"TEXT"` and `"BINARY"` respectively, so `StorageType.TEXT.value == "TEXT"`
4. The enum extends `str` and `enum.Enum` (i.e., `class StorageType(str, Enum)`) so that `StorageType.TEXT == "TEXT"` evaluates to `True` for backward compatibility
5. Export `StorageType` from `cfinterface/__init__.py`

### Inputs/Props

N/A -- this ticket only creates the enum definition.

### Outputs/Behavior

After this ticket:

- `from cfinterface.storage import StorageType` works
- `from cfinterface import StorageType` works
- `StorageType.TEXT` has value `"TEXT"`
- `StorageType.BINARY` has value `"BINARY"`
- `StorageType.TEXT == "TEXT"` is `True` (str enum comparison)
- `StorageType("TEXT")` returns `StorageType.TEXT`
- `StorageType("BINARY")` returns `StorageType.BINARY`

### Error Handling

- `StorageType("INVALID")` raises `ValueError` -- standard enum behavior

## Acceptance Criteria

- [ ] Given `cfinterface/storage.py` exists, when inspected, then it contains `class StorageType(str, Enum)` with `TEXT = "TEXT"` and `BINARY = "BINARY"`
- [ ] Given `StorageType.TEXT`, when compared with `==` to `"TEXT"`, then it returns `True`
- [ ] Given `StorageType.BINARY`, when compared with `==` to `"BINARY"`, then it returns `True`
- [ ] Given `StorageType("TEXT")`, when called, then it returns `StorageType.TEXT`
- [ ] Given `from cfinterface import StorageType`, when executed, then it succeeds
- [ ] Given the full test suite, when `pytest tests/` is run, then all existing tests pass (no regressions from adding the new module)

## Implementation Guide

### Suggested Approach

Create `cfinterface/storage.py`:

```python
from enum import Enum


class StorageType(str, Enum):
    """
    Enum for the storage type of a file, determining whether
    the file is read/written in text or binary mode.

    Using ``str`` as a mixin ensures backward compatibility:
    ``StorageType.TEXT == "TEXT"`` evaluates to ``True``.
    """

    TEXT = "TEXT"
    BINARY = "BINARY"
```

Then update `cfinterface/__init__.py` to export it:

```python
"""
cfi
====

cfi is a Python module for handling custom formatted files
and provide reading, storing and writing utilities.
"""

__version__ = "1.9.0"

from . import components  # noqa
from . import data  # noqa
from . import reading  # noqa
from . import writing  # noqa
from . import files  # noqa
from .storage import StorageType  # noqa
```

### Key Files to Modify

- `cfinterface/storage.py` (new file)
- `cfinterface/__init__.py` (add export)

### Patterns to Follow

- `str, Enum` mixin pattern is the standard Python approach for string-valued enums that need to compare equal to their string values
- Single responsibility: this module contains only the enum, no logic

### Pitfalls to Avoid

- Do NOT use `enum.StrEnum` (Python 3.11+) since the project requires Python 3.10+
- Do NOT add any factory logic to this module -- that stays in the adapter repositories
- Do NOT modify any existing files other than `__init__.py` -- integration is done in tickets 007-009

## Testing Requirements

### Unit Tests

Create `tests/test_storage.py`:

```python
from cfinterface.storage import StorageType


def test_storage_type_text_value():
    assert StorageType.TEXT.value == "TEXT"


def test_storage_type_binary_value():
    assert StorageType.BINARY.value == "BINARY"


def test_storage_type_text_str_comparison():
    assert StorageType.TEXT == "TEXT"


def test_storage_type_binary_str_comparison():
    assert StorageType.BINARY == "BINARY"


def test_storage_type_from_string():
    assert StorageType("TEXT") is StorageType.TEXT
    assert StorageType("BINARY") is StorageType.BINARY


def test_storage_type_import_from_package():
    from cfinterface import StorageType as ST
    assert ST.TEXT == "TEXT"
```

### Integration Tests

Run `pytest tests/` to verify no regressions.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None
- **Blocks**: ticket-007, ticket-008, ticket-009

## Effort Estimate

**Points**: 1
**Confidence**: High
