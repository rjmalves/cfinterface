# ticket-001 Create Native Null-Checking Utility Function

## Context

### Background

cfinterface v1.8.3 imports `pandas` at module level in all four Field subclasses (`FloatField`, `IntegerField`, `LiteralField`, `DatetimeField`) solely for `pd.isnull()` null detection. This creates a heavy runtime dependency (~150MB) for a trivial check. The framework needs a lightweight replacement that handles the same value types without pandas.

### Relation to Epic

This is the foundational ticket of Epic 01 (Remove pandas dependency). All subsequent tickets in this epic depend on this utility function existing before the `pd.isnull()` calls can be replaced.

### Current State

The file `cfinterface/_utils/__init__.py` exists but is empty (0 bytes). There is no null-checking utility in the codebase. Every Field subclass uses `pd.isnull()` in their `_binary_write()` and `_textual_write()` methods.

## Specification

### Requirements

Create a function `_is_null(value: Any) -> bool` in `cfinterface/_utils/__init__.py` that:

1. Returns `True` for `None`
2. Returns `True` for `float('nan')`
3. Returns `True` for `numpy.nan` (which is `float('nan')` but passed through numpy code paths)
4. Returns `True` for `numpy.float64('nan')` and other numpy NaN-typed values
5. Returns `False` for any normal numeric value (int, float, numpy scalar)
6. Returns `False` for any string value (including empty string)
7. Returns `False` for any datetime value
8. Does NOT import pandas

### Inputs/Props

- `value: Any` -- the value to check for null/NaN

### Outputs/Behavior

- Returns `bool` -- `True` if the value is null-like (None or NaN), `False` otherwise

### Error Handling

- Must never raise an exception. For any unexpected input type, return `False` (matching the behavior of `pd.isnull()` which returns `False` for non-null-like values).

## Acceptance Criteria

- [ ] Given `None` is passed to `_is_null()`, when called, then it returns `True`
- [ ] Given `float('nan')` is passed to `_is_null()`, when called, then it returns `True`
- [ ] Given `numpy.nan` is passed to `_is_null()`, when called, then it returns `True`
- [ ] Given `numpy.float64('nan')` is passed to `_is_null()`, when called, then it returns `True`
- [ ] Given `0.0` is passed to `_is_null()`, when called, then it returns `False`
- [ ] Given `42` is passed to `_is_null()`, when called, then it returns `False`
- [ ] Given `""` (empty string) is passed to `_is_null()`, when called, then it returns `False`
- [ ] Given a `datetime` object is passed to `_is_null()`, when called, then it returns `False`
- [ ] Given `numpy.float32(1.5)` is passed to `_is_null()`, when called, then it returns `False`
- [ ] The function does not import pandas anywhere in its implementation
- [ ] The function is importable as `from cfinterface._utils import _is_null`

## Implementation Guide

### Suggested Approach

The implementation should use `math.isnan()` for float/numpy NaN detection and a type check for `None`:

```python
import math
from typing import Any


def _is_null(value: Any) -> bool:
    """Check if a value is null-like (None or NaN).

    Replaces pd.isnull() for the specific use cases in cfinterface
    Field subclasses, without requiring a pandas dependency.

    :param value: The value to check
    :type value: Any
    :return: True if the value is None or NaN
    :rtype: bool
    """
    if value is None:
        return True
    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        return False
```

Key insight: `math.isnan()` works with both Python `float('nan')` and numpy NaN types (`numpy.nan`, `numpy.float64('nan')`, etc.) because numpy scalars implement `__float__()`. The `try/except` handles types that don't support `isnan` (strings, datetime, etc.).

### Key Files to Modify

- `cfinterface/_utils/__init__.py` -- add the `_is_null()` function

### Patterns to Follow

- Use `__slots__` where applicable (not relevant here, it is a module-level function)
- Use numpy docstring format consistent with the rest of the codebase
- Keep the function private (underscore prefix) since it is an internal utility

### Pitfalls to Avoid

- Do NOT use `value != value` as a NaN check -- it works for float NaN but is confusing and may have edge cases with custom `__eq__` implementations
- Do NOT import pandas anywhere in this function
- Do NOT try to handle `pandas.NaT` or `pandas.NA` -- those are pandas-specific and only relevant if pandas is installed (which this function aims to avoid)
- `math.isnan()` raises `TypeError` for non-numeric types, so the try/except is mandatory

## Testing Requirements

### Unit Tests

Create `tests/_utils/test_is_null.py` (create the `tests/_utils/` directory with `__init__.py`):

```python
import math
from datetime import datetime
import numpy as np
from cfinterface._utils import _is_null


def test_is_null_none():
    assert _is_null(None) is True

def test_is_null_float_nan():
    assert _is_null(float('nan')) is True

def test_is_null_numpy_nan():
    assert _is_null(np.nan) is True

def test_is_null_numpy_float64_nan():
    assert _is_null(np.float64('nan')) is True

def test_is_null_numpy_float32_nan():
    assert _is_null(np.float32('nan')) is True

def test_is_null_zero():
    assert _is_null(0.0) is False

def test_is_null_integer():
    assert _is_null(42) is False

def test_is_null_negative():
    assert _is_null(-1.5) is False

def test_is_null_empty_string():
    assert _is_null("") is False

def test_is_null_string():
    assert _is_null("hello") is False

def test_is_null_datetime():
    assert _is_null(datetime(2024, 1, 1)) is False

def test_is_null_numpy_scalar():
    assert _is_null(np.float32(1.5)) is False

def test_is_null_numpy_int():
    assert _is_null(np.int32(10)) is False
```

### Integration Tests

Not applicable for this ticket -- integration is tested in ticket-002 when the utility replaces `pd.isnull()`.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None
- **Blocks**: ticket-002

## Effort Estimate

**Points**: 1
**Confidence**: High
