# ticket-003 Convert RegisterFile.\_as_df() to Lazy pandas Import

## Context

### Background

`RegisterFile` in `cfinterface/files/registerfile.py` imports pandas at module level (`import pandas as pd`) for the `_as_df()` convenience method that converts registers to a DataFrame. After ticket-002 removed pandas from all Field subclasses, this is the last remaining module-level pandas import in the codebase.

### Relation to Epic

This is the third ticket in Epic 01. It converts the last pandas usage to a lazy import, making pandas fully optional for the core framework. This must be done before ticket-004 moves pandas to optional dependencies.

### Current State

`cfinterface/files/registerfile.py` line 3: `import pandas as pd  # type: ignore`

The `_as_df()` method (lines 44-61) uses `pd.DataFrame()` twice:

- Line 57: `return pd.DataFrame()` (empty DataFrame when no registers found)
- Lines 59-60: `return pd.DataFrame(data={...})` (DataFrame from register properties)

No other method in `RegisterFile` uses pandas.

## Specification

### Requirements

1. Remove `import pandas as pd` from the top of `registerfile.py`
2. Convert `_as_df()` to use a lazy import: `import pandas as pd` inside the method body
3. If pandas is not installed, raise `ImportError` with a helpful message: `"pandas is required for _as_df(). Install it with: pip install cfinterface[pandas]"`
4. No other changes to `RegisterFile`

### Inputs/Props

N/A -- `_as_df()` takes `register_type: Type[Register]` and returns `pd.DataFrame`. Its signature does not change.

### Outputs/Behavior

- When pandas is installed: identical behavior to current implementation
- When pandas is NOT installed: `_as_df()` raises `ImportError` with installation instructions

### Error Handling

`ImportError` is raised with a clear message when pandas is not available. This is the standard Python pattern for optional dependencies.

## Acceptance Criteria

- [ ] Given `cfinterface/files/registerfile.py`, when inspected, then the top-level imports do NOT contain `import pandas`
- [ ] Given `_as_df()` method, when inspected, then it contains `import pandas as pd` inside the method body (lazy import)
- [ ] Given pandas IS installed, when `_as_df()` is called with a valid register type, then it returns a `pd.DataFrame` (existing behavior preserved)
- [ ] Given pandas IS installed, when `_as_df()` is called with a register type that has no instances, then it returns an empty `pd.DataFrame`
- [ ] Given all existing tests are run with pandas installed, when `pytest tests/` executes, then all tests pass
- [ ] Given the `_as_df()` method, when inspected, then it catches `ImportError` and re-raises with a message containing `"pip install cfinterface[pandas]"`

## Implementation Guide

### Suggested Approach

Replace the module-level import with a lazy import inside `_as_df()`:

```python
def _as_df(self, register_type: Type[Register]):
    """
    Converts the registers of a given type to a dataframe for enabling
    read-only tasks. Changing the dataframe does not affect
    the file registers.

    :param register_type: The register_type to be converted
    :type register_type: Type[:class:`Register`]
    :return: The converted registers
    :rtype: pd.DataFrame
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for _as_df(). "
            "Install it with: pip install cfinterface[pandas]"
        )
    registers = [b for b in self.data.of_type(register_type)]
    if len(registers) == 0:
        return pd.DataFrame()
    cols = registers[0].custom_properties
    return pd.DataFrame(
        data={c: [getattr(r, c) for r in registers] for c in cols}
    )
```

Also remove the `import pandas as pd  # type: ignore` from line 3 of the file. The remaining imports on lines 1-2 and 5-9 stay unchanged.

### Key Files to Modify

- `cfinterface/files/registerfile.py`

### Patterns to Follow

- Lazy import pattern: `try: import X except ImportError: raise ImportError("...")`
- Keep the same method signature and docstring format

### Pitfalls to Avoid

- Do NOT remove the `pd.DataFrame` type hint from the docstring -- it is documentation, not a runtime type check
- Do NOT add `pandas` as an import anywhere else in the file
- The return type annotation references `pd.DataFrame` -- since pd is no longer imported at module level, change the return annotation to use a string literal or just remove it (the method already has no return type annotation, only the docstring mentions it)

## Testing Requirements

### Unit Tests

The existing test file `tests/files/test_registerfile.py` already tests `_as_df()` indirectly. Add an explicit test:

```python
def test_registerfile_as_df_requires_pandas():
    """Verify _as_df works when pandas is available."""
    # This test verifies the lazy import path works correctly
    # when pandas IS installed (which it is in the test env)
    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.components.register import Register
    rf = RegisterFile()
    result = rf._as_df(Register)
    # Should return empty DataFrame for no matching registers
    import pandas as pd
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
```

### Integration Tests

Run `pytest tests/` to verify all existing tests pass.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-002
- **Blocks**: ticket-004

## Effort Estimate

**Points**: 1
**Confidence**: High
