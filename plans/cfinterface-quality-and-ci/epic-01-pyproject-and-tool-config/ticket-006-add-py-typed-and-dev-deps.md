# ticket-006 Add py.typed Marker and New Dev Dependencies

## Context

### Background

cfinterface provides type annotations but lacks the `py.typed` marker file required by PEP 561 for type checkers to recognize it as a typed package. Additionally, the dev dependencies need to include `hypothesis` (property-based testing, Epic 3), `pytest-benchmark` (benchmark integration, Epic 3), and `pandas-stubs` (mypy pandas stub types) to support the work in subsequent epics.

### Relation to Epic

Final ticket in Epic 1. Adds the PEP 561 compliance marker and prepares dev dependencies for Epics 2-3.

### Current State

- No `cfinterface/py.typed` file exists
- Dev dependencies in pyproject.toml (lines 30-42):
  ```toml
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
- Missing: `hypothesis`, `pytest-benchmark`, `pandas-stubs`

## Specification

### Requirements

1. Create an empty `cfinterface/py.typed` marker file (PEP 561)
2. Ensure `py.typed` is included in the wheel by verifying the `[tool.hatch.build.targets.wheel]` include pattern `"cfinterface/"` covers it
3. Add `hypothesis` to dev dependencies
4. Add `pytest-benchmark` to dev dependencies
5. Add `pandas-stubs` to dev dependencies

### Inputs/Props

- File: `/home/rogerio/git/cfinterface/pyproject.toml`
- New file: `/home/rogerio/git/cfinterface/cfinterface/py.typed`

### Outputs/Behavior

Create `/home/rogerio/git/cfinterface/cfinterface/py.typed` as an empty file.

Update the dev dependencies in pyproject.toml:

```toml
dev = [
    "pandas>=2.2.3",
    "pandas-stubs",
    "pytest",
    "pytest-benchmark",
    "pytest-cov",
    "hypothesis",
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

### Error Handling

Not applicable — file creation and dependency addition only.

## Acceptance Criteria

- [ ] Given the path `/home/rogerio/git/cfinterface/cfinterface/py.typed`, when checking file existence with `test -f cfinterface/py.typed`, then the file exists
- [ ] Given the file `/home/rogerio/git/cfinterface/cfinterface/py.typed`, when checking its content, then it is empty (0 bytes)
- [ ] Given the file `/home/rogerio/git/cfinterface/pyproject.toml`, when inspecting `[project.optional-dependencies]` dev list, then it contains `"hypothesis"`, `"pytest-benchmark"`, and `"pandas-stubs"`
- [ ] Given the updated pyproject.toml, when running `uv sync --all-extras --dev`, then all dependencies install successfully
- [ ] Given the updated pyproject.toml, when running `uv run python -c "import hypothesis; import pytest_benchmark; import pandas"`, then all imports succeed

## Implementation Guide

### Suggested Approach

1. Create the empty file: `touch cfinterface/py.typed`
2. Verify it will be included in the wheel: the existing `[tool.hatch.build.targets.wheel]` has `include = ["cfinterface/"]`, which includes all files under `cfinterface/`, so `py.typed` is automatically covered
3. Edit `/home/rogerio/git/cfinterface/pyproject.toml` to add the three new dev dependencies
4. Run `uv sync --all-extras --dev` to install the new dependencies
5. Verify imports work

### Key Files to Modify

- `/home/rogerio/git/cfinterface/cfinterface/py.typed` (create, empty)
- `/home/rogerio/git/cfinterface/pyproject.toml` (dev dependencies)

### Patterns to Follow

- Keep dev dependencies alphabetically ordered by package name within the list
- The py.typed file must be completely empty (not even a newline) per PEP 561

### Pitfalls to Avoid

- Do NOT put py.typed in the project root — it must be inside the package directory (`cfinterface/`)
- Do NOT add version pins for hypothesis or pytest-benchmark unless there is a specific compatibility issue — let the resolver handle it
- Do NOT add hypothesis or pytest-benchmark to the main `dependencies` list — they are dev-only
- Do NOT forget to run `uv sync` after modifying dependencies — the lockfile needs updating

## Testing Requirements

### Unit Tests

Not applicable — file creation and dependency change only.

### Integration Tests

- Run `uv sync --all-extras --dev` — must succeed
- Run `uv run python -c "import hypothesis; import pytest_benchmark; import pandas"` — must succeed
- Run `uv run mypy ./cfinterface` — must still pass (pandas-stubs resolves the `import-untyped` issue)
- Run `test -f cfinterface/py.typed && echo "exists"` — must print "exists"

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-001-update-classifiers-and-metadata (Typing :: Typed classifier should be in place)
- **Blocks**: ticket-012-add-hypothesis-field-tests (needs hypothesis installed), ticket-014-migrate-to-pytest-benchmark (needs pytest-benchmark installed)

## Effort Estimate

**Points**: 1
**Confidence**: High
