# ticket-006 Update conf.py language and intersphinx settings

## Context

### Background

The cfinterface Sphinx configuration has `language = "en_US"` but the downstream audience is Brazilian Portuguese-speaking. The intersphinx mapping for pandas uses an HTTP URL instead of HTTPS, and the Python intersphinx URL uses a dynamic format string that could break. These should be cleaned up alongside the language change.

### Relation to Epic

This is the third and final ticket in Epic 02 (Sphinx Modernization). It completes the Sphinx configuration cleanup after the theme migration.

### Current State

File `/home/rogerio/git/cfinterface/docs/source/conf.py`:

- Line 63: `language = "en_US"`
- Lines 111-118: `intersphinx_mapping` with:
  - `"python"` using `"https://docs.python.org/{.major}".format(sys.version_info)` (dynamic, fragile)
  - `"pandas"` using `"http://pandas.pydata.org/pandas-docs/stable/"` (HTTP, not HTTPS)
  - `"numpy"` using `"https://numpy.org/doc/stable/"` (correct)
- Line 77: `exclude_patterns: List[str] = []` uses deprecated `typing.List` annotation

## Specification

### Requirements

1. Change `language = "en_US"` to `language = "pt_BR"` in `conf.py`
2. Update intersphinx mappings:
   - Python: change to `"https://docs.python.org/3/"` (stable, not version-dependent)
   - pandas: change to `"https://pandas.pydata.org/pandas-docs/stable/"` (HTTPS)
   - numpy: keep as-is (already correct)
3. Replace `List[str]` with `list[str]` on the `exclude_patterns` line (PEP 585, Python >= 3.10)
4. Remove the `from typing import List` import if no longer needed

### Inputs/Props

Current `conf.py` at `/home/rogerio/git/cfinterface/docs/source/conf.py`.

### Outputs/Behavior

- Sphinx builds with `pt_BR` language setting
- Intersphinx links resolve correctly for Python, pandas, and numpy documentation
- No `typing.List` usage remains in `conf.py`

### Error Handling

- If intersphinx URLs are incorrect, Sphinx will emit warnings (caught by `-W` flag)

## Acceptance Criteria

- [ ] Given `docs/source/conf.py`, when the `language` variable is read, then its value is `"pt_BR"`
- [ ] Given `docs/source/conf.py`, when the `intersphinx_mapping["python"]` URL is read, then it is `"https://docs.python.org/3/"`
- [ ] Given `docs/source/conf.py`, when the `intersphinx_mapping["pandas"]` URL is read, then it starts with `"https://"`
- [ ] Given `docs/source/conf.py`, when the file is searched for `from typing import List`, then no match is found
- [ ] Given a clean install, when `uv run python -m sphinx -M html docs/source docs/build -W` is executed, then the exit code is 0

## Implementation Guide

### Suggested Approach

1. Change `language = "en_US"` to `language = "pt_BR"`
2. Replace the `intersphinx_mapping` dict:
   ```python
   intersphinx_mapping = {
       "python": ("https://docs.python.org/3/", None),
       "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
       "numpy": ("https://numpy.org/doc/stable/", None),
   }
   ```
3. Change `exclude_patterns: List[str] = []` to `exclude_patterns: list[str] = []`
4. Remove `from typing import List` import
5. Run `uv run python -m sphinx -M html docs/source docs/build -W` to verify

### Key Files to Modify

- `/home/rogerio/git/cfinterface/docs/source/conf.py` (MODIFY)

### Patterns to Follow

Use built-in generics (`list[str]`) instead of `typing.List[str]` -- the project targets Python >= 3.10 where this is supported.

### Pitfalls to Avoid

- Do NOT change `language` to `"pt-BR"` (hyphen) -- Sphinx uses underscore format: `"pt_BR"`
- Do NOT remove the `sys` import -- it is still used by `sys.path.insert`
- Do NOT change `source_encoding` or `source_suffix` -- these are independent of language
- Verify the pandas intersphinx URL works (the canonical URL changed from `pandas.pydata.org` to `pandas.pydata.org` with HTTPS)

## Testing Requirements

### Unit Tests

Not applicable.

### Integration Tests

- Run `uv run python -m sphinx -M html docs/source docs/build -W` and verify exit code 0
- Verify intersphinx references resolve by checking Sphinx output for "loading intersphinx inventory" messages

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-004-migrate-sphinx-theme-to-furo.md (this ticket modifies the same conf.py file)
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: High
