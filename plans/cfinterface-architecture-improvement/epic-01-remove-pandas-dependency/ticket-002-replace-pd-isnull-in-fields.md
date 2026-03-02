# ticket-002 Replace pd.isnull() in All Field Subclasses

## Context

### Background

All four Field subclasses in cfinterface import pandas at module level and use `pd.isnull()` in their write methods. After ticket-001 created the `_is_null()` utility function, this ticket replaces every `pd.isnull()` call and removes the `import pandas` statements from these files.

### Relation to Epic

This is the core ticket of Epic 01. It performs the actual replacement of pandas usage in the Field layer -- the most impacted part of the codebase. After this ticket, only `RegisterFile._as_df()` will still reference pandas.

### Current State

Each of the four Field subclasses has `import pandas as pd` at the top and uses `pd.isnull()` in their `_binary_write()` and/or `_textual_write()` methods:

- **FloatField** (`cfinterface/components/floatfield.py`, line 2): `import pandas as pd`
  - Line 62: `if self.value is None or pd.isnull(self.value):` in `_binary_write()`
  - Line 70: `if self.value is not None and not pd.isnull(self.value):` in `_textual_write()`

- **IntegerField** (`cfinterface/components/integerfield.py`, line 2): `import pandas as pd`
  - Line 48: `if self.value is None or pd.isnull(self.value):` in `_binary_write()`
  - Line 55: `if self.value is None or pd.isnull(self.value):` in `_textual_write()`

- **LiteralField** (`cfinterface/components/literalfield.py`, line 2): `import pandas as pd`
  - Line 36: `if self.value is None or pd.isnull(self.value):` in `_binary_write()`
  - Line 43: `if self.value is None or pd.isnull(self.value):` in `_textual_write()`

- **DatetimeField** (`cfinterface/components/datetimefield.py`, line 2): `import pandas as pd`
  - Line 67: `if self.value is None or pd.isnull(self.value):` in `_binary_write()`
  - Line 79: `if self.value is None or pd.isnull(self.value):` in `_textual_write()`

## Specification

### Requirements

1. Remove `import pandas as pd` from all four Field subclass files
2. Add `from cfinterface._utils import _is_null` to each file
3. Replace every `pd.isnull(self.value)` call with `_is_null(self.value)`
4. Preserve exact behavior: `self.value is None or _is_null(self.value)` is equivalent to `self.value is None or pd.isnull(self.value)` for all value types these fields encounter (int, float, str, datetime, None, NaN)

### Inputs/Props

N/A -- this is a refactoring ticket with no API changes.

### Outputs/Behavior

All Field subclass write methods behave identically before and after the change. The only observable difference is that `import cfinterface.components.floatfield` (and siblings) no longer triggers a pandas import.

### Error Handling

No change to error handling. The `_is_null()` function handles the same edge cases as `pd.isnull()` for the value types used by these fields.

## Acceptance Criteria

- [ ] Given `cfinterface/components/floatfield.py`, when inspected, then it does NOT contain `import pandas` or `pd.isnull`
- [ ] Given `cfinterface/components/integerfield.py`, when inspected, then it does NOT contain `import pandas` or `pd.isnull`
- [ ] Given `cfinterface/components/literalfield.py`, when inspected, then it does NOT contain `import pandas` or `pd.isnull`
- [ ] Given `cfinterface/components/datetimefield.py`, when inspected, then it does NOT contain `import pandas` or `pd.isnull`
- [ ] Given all four files, when inspected, then each contains `from cfinterface._utils import _is_null`
- [ ] Given the existing test `test_floatfield_write()`, when run, then it passes unchanged
- [ ] Given the existing test `test_floatfield_write_empty()`, when run, then it passes unchanged
- [ ] Given the existing test `test_floatfield_write_binary()`, when run, then it passes unchanged
- [ ] Given the existing test `test_floatfield_write_empty_binary()`, when run, then it passes unchanged
- [ ] Given the existing test `test_integerfield_write()`, when run, then it passes unchanged
- [ ] Given the existing test `test_integerfield_write_empty()`, when run, then it passes unchanged
- [ ] Given the existing test `test_integerfield_write_binary()`, when run, then it passes unchanged
- [ ] Given all 25 existing test files, when `pytest tests/` is run, then all tests pass
- [ ] Given a new test that creates a FloatField with `value=float('nan')` and calls `_textual_write()`, when run, then it returns a right-justified empty string (same as None behavior)
- [ ] Given a new test that creates an IntegerField with `value=float('nan')` and calls `_textual_write()`, when run, then it returns a right-justified empty string (same as None behavior)

## Implementation Guide

### Suggested Approach

For each of the four files, perform these exact edits:

**Step 1**: In `cfinterface/components/floatfield.py`:

- Remove line 2: `import pandas as pd  # type: ignore`
- Add after remaining imports: `from cfinterface._utils import _is_null`
- Line 62: Change `if self.value is None or pd.isnull(self.value):` to `if self.value is None or _is_null(self.value):`
- Line 70: Change `if self.value is not None and not pd.isnull(self.value):` to `if self.value is not None and not _is_null(self.value):`

**Step 2**: In `cfinterface/components/integerfield.py`:

- Remove line 2: `import pandas as pd  # type: ignore`
- Add after remaining imports: `from cfinterface._utils import _is_null`
- Line 48: Change `pd.isnull(self.value)` to `_is_null(self.value)`
- Line 55: Change `pd.isnull(self.value)` to `_is_null(self.value)`

**Step 3**: In `cfinterface/components/literalfield.py`:

- Remove line 2: `import pandas as pd  # type: ignore`
- Add: `from cfinterface._utils import _is_null`
- Line 36: Change `pd.isnull(self.value)` to `_is_null(self.value)`
- Line 43: Change `pd.isnull(self.value)` to `_is_null(self.value)`

**Step 4**: In `cfinterface/components/datetimefield.py`:

- Remove line 2: `import pandas as pd  # type: ignore`
- Add: `from cfinterface._utils import _is_null`
- Line 67: Change `pd.isnull(self.value)` to `_is_null(self.value)`
- Line 79: Change `pd.isnull(self.value)` to `_is_null(self.value)`

### Key Files to Modify

- `cfinterface/components/floatfield.py`
- `cfinterface/components/integerfield.py`
- `cfinterface/components/literalfield.py`
- `cfinterface/components/datetimefield.py`

### Patterns to Follow

- Keep the same `self.value is None or _is_null(self.value)` guard pattern (the `is None` check is a fast path before the function call)
- Preserve exact formatting and line structure -- only change the import and the function name

### Pitfalls to Avoid

- Do NOT simplify `self.value is None or _is_null(self.value)` to just `_is_null(self.value)` even though `_is_null` handles `None`. The explicit `is None` check is a fast path and makes intent clear.
- Do NOT change any read methods -- only write methods use `pd.isnull()`
- Do NOT modify `cfinterface/files/registerfile.py` in this ticket -- that is ticket-003

## Testing Requirements

### Unit Tests

Add NaN-specific write tests to the existing test files. Add these to the bottom of each respective test file:

In `tests/components/test_floatfield.py`:

```python
def test_floatfield_write_nan_textual():
    field = FloatField(5, 0, 1, value=float('nan'))
    result = field.write("")
    assert result.strip() == ""
    assert len(result) == 5

def test_floatfield_write_nan_binary():
    field = FloatField(4, 0, value=float('nan'))
    result = field.write(b"")
    # NaN should write as 0.0 in binary
    assert len(result) == 4
```

In `tests/components/test_integerfield.py`:

```python
def test_integerfield_write_nan_textual():
    field = IntegerField(5, 0, value=float('nan'))
    result = field.write("")
    assert result.strip() == ""
    assert len(result) == 5

def test_integerfield_write_nan_binary():
    field = IntegerField(4, 0, value=float('nan'))
    result = field.write(b"")
    assert len(result) == 4
```

### Integration Tests

Run `pytest tests/` to verify all 25 existing test files still pass.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-001
- **Blocks**: ticket-003, ticket-004

## Effort Estimate

**Points**: 2
**Confidence**: High
