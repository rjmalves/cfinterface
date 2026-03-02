# ticket-001 Update Python Classifiers and Project Metadata

## Context

### Background

cfinterface v1.9.0 supports Python 3.10+ (`requires-python = ">= 3.10"`) and has been tested locally on Python 3.14. However, the pyproject.toml classifiers only list Python 3.10, missing 3.11 through 3.14. The development status is "4 - Beta" but the library is stable and in production use. The classifiers need to accurately reflect supported Python versions for PyPI discoverability.

### Relation to Epic

This is the first ticket in Epic 1 (pyproject.toml hardening). It handles the simplest, most mechanical changes: classifiers and metadata. Other tickets in this epic build on this by adding tool configuration sections.

### Current State

The file `/home/rogerio/git/cfinterface/pyproject.toml` has these classifiers (lines 18-24):

```toml
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Operating System :: OS Independent",
]
```

Only Python 3.10 is listed. Python 3.11, 3.12, 3.13, and 3.14 are missing.

## Specification

### Requirements

1. Add Python version classifiers for 3.11, 3.12, 3.13, and 3.14
2. Add the generic `Programming Language :: Python :: 3` classifier
3. Add `Typing :: Typed` classifier (anticipating py.typed in ticket-006)

### Inputs/Props

- File: `/home/rogerio/git/cfinterface/pyproject.toml`

### Outputs/Behavior

The classifiers section should become:

```toml
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Operating System :: OS Independent",
    "Typing :: Typed",
]
```

### Error Handling

Not applicable — this is a metadata-only change.

## Acceptance Criteria

- [ ] Given the file `/home/rogerio/git/cfinterface/pyproject.toml`, when inspecting the `classifiers` list, then it contains `"Programming Language :: Python :: 3.11"`, `"Programming Language :: Python :: 3.12"`, `"Programming Language :: Python :: 3.13"`, and `"Programming Language :: Python :: 3.14"`
- [ ] Given the file `/home/rogerio/git/cfinterface/pyproject.toml`, when inspecting the `classifiers` list, then it contains `"Programming Language :: Python :: 3"` and `"Typing :: Typed"`
- [ ] Given the updated pyproject.toml, when running `uv run python -c "import cfinterface"`, then the import succeeds without errors

## Implementation Guide

### Suggested Approach

1. Open `/home/rogerio/git/cfinterface/pyproject.toml`
2. Replace the classifiers list with the expanded version shown in Outputs/Behavior
3. Verify the file is valid TOML by running `uv sync --dry-run`

### Key Files to Modify

- `/home/rogerio/git/cfinterface/pyproject.toml` (lines 18-24)

### Patterns to Follow

- Keep classifiers alphabetically grouped by category (Development Status, then Intended Audience, then License, then Programming Language, then Operating System, then Typing)
- Use 4-space indentation for TOML arrays as in the existing file

### Pitfalls to Avoid

- Do NOT change `requires-python = ">= 3.10"` — this stays as-is
- Do NOT change `Development Status :: 4 - Beta` — that decision is out of scope
- Do NOT add classifiers for Python versions below 3.10

## Testing Requirements

### Unit Tests

Not applicable — metadata-only change.

### Integration Tests

- Run `uv sync --dry-run` to verify valid TOML
- Run `uv run python -c "import cfinterface"` to verify no import regressions

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None
- **Blocks**: ticket-006-add-py-typed-and-dev-deps (Typing :: Typed classifier anticipates py.typed)

## Effort Estimate

**Points**: 1
**Confidence**: High
