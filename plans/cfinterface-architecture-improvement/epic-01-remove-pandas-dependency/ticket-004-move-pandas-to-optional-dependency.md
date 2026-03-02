# ticket-004 Move pandas to Optional Dependency in pyproject.toml

## Context

### Background

After tickets 001-003, no module in cfinterface imports pandas at the module level. The only remaining usage is a lazy import inside `RegisterFile._as_df()`. pandas can now be safely moved from the required `dependencies` list to `[project.optional-dependencies]`.

### Relation to Epic

This is the final ticket in Epic 01. It makes the dependency change official in the package metadata, completing the pandas removal. After this ticket, installing cfinterface will NOT install pandas unless explicitly requested.

### Current State

`pyproject.toml` lines 8-11:

```toml
dependencies = [
    "numpy>=2.0.0",
    "pandas>=2.2.3",
]
```

Lines 27-38:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "ruff",
    "mypy",
    "sphinx-rtd-theme",
    "sphinx-gallery",
    "sphinx",
    "numpydoc",
    "plotly",
    "matplotlib",
]
```

## Specification

### Requirements

1. Remove `"pandas>=2.2.3"` from the `dependencies` list
2. Add a new optional dependency group `pandas` with `"pandas>=2.2.3"`
3. Add pandas to the `dev` optional dependency group (so dev/test environments still have it)
4. Bump the version in `cfinterface/__init__.py` from `1.8.3` to `1.9.0` (minor version bump since this is a dependency change that affects consumers)

### Inputs/Props

N/A -- this is a packaging change.

### Outputs/Behavior

- `pip install cfinterface` installs only numpy (no pandas)
- `pip install cfinterface[pandas]` installs cfinterface + pandas
- `pip install cfinterface[dev]` installs cfinterface + all dev dependencies including pandas

### Error Handling

N/A.

## Acceptance Criteria

- [ ] Given `pyproject.toml`, when inspected, then `dependencies` contains only `"numpy>=2.0.0"`
- [ ] Given `pyproject.toml`, when inspected, then `[project.optional-dependencies]` contains a `pandas` group with `"pandas>=2.2.3"`
- [ ] Given `pyproject.toml`, when inspected, then the `dev` group includes `"pandas>=2.2.3"`
- [ ] Given `cfinterface/__init__.py`, when inspected, then `__version__` is `"1.9.0"`
- [ ] Given a fresh virtual environment with only cfinterface installed (no pandas), when `python -c "import cfinterface"` is run, then it succeeds without error
- [ ] Given a fresh virtual environment with cfinterface[pandas] installed, when the full test suite is run, then all tests pass

## Implementation Guide

### Suggested Approach

**Step 1**: Edit `pyproject.toml`:

```toml
[project]
name = "cfinterface"
dynamic = ["version"]
dependencies = [
    "numpy>=2.0.0",
]
requires-python = ">= 3.10"
# ... rest unchanged ...

[project.optional-dependencies]
pandas = [
    "pandas>=2.2.3",
]
dev = [
    "pandas>=2.2.3",
    "pytest",
    "pytest-cov",
    "ruff",
    "mypy",
    "sphinx-rtd-theme",
    "sphinx-gallery",
    "sphinx",
    "numpydoc",
    "plotly",
    "matplotlib",
]
```

**Step 2**: Edit `cfinterface/__init__.py` line 9:

```python
__version__ = "1.9.0"
```

### Key Files to Modify

- `pyproject.toml`
- `cfinterface/__init__.py`

### Patterns to Follow

- Optional dependency group naming: use the package name (`pandas`) as the group name
- Include pandas in `dev` so the test environment always has it

### Pitfalls to Avoid

- Do NOT remove pandas from the `dev` group -- tests need it for `_as_df()` testing
- Do NOT forget to bump the version -- this is a behavioral change that downstream consumers need to know about
- The version bump should be minor (1.8.3 -> 1.9.0) not major, since existing code still works if pandas is installed

## Testing Requirements

### Unit Tests

No new unit tests. This is a packaging change.

### Integration Tests

Verify the full test suite passes with `pytest tests/` after the change. The test environment should have pandas installed via the `dev` extra.

### E2E Tests

Manual verification: in a clean virtual environment, install cfinterface without pandas and verify `import cfinterface` succeeds.

## Dependencies

- **Blocked By**: ticket-002, ticket-003
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: High
