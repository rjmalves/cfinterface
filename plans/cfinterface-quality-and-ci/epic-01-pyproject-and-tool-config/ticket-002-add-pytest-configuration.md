# ticket-002 Add pytest Configuration to pyproject.toml

## Context

### Background

cfinterface runs pytest with command-line flags only (`uv run pytest --cov-report=xml --cov=cfinterface ./tests`). There is no `[tool.pytest.ini_options]` section in pyproject.toml, which means: no registered markers (pytest emits warnings for custom markers), no default addopts, no test path configuration, and no coverage fail-under enforcement. This ticket adds the pytest configuration section.

### Relation to Epic

Second ticket in Epic 1. Establishes pytest configuration that will be referenced by the CI workflows (Epic 2) and used by the test infrastructure (Epic 3). The markers registered here (`slow`, `benchmark`) will be used in subsequent tickets.

### Current State

- `/home/rogerio/git/cfinterface/pyproject.toml` has NO `[tool.pytest.ini_options]` section
- Tests are run with: `uv run pytest --cov-report=xml --cov=cfinterface ./tests`
- No markers are registered
- No `--cov-fail-under` enforcement
- 392 tests, all passing, 94% coverage

## Specification

### Requirements

1. Add `[tool.pytest.ini_options]` section to pyproject.toml
2. Set `testpaths = ["tests"]`
3. Set `addopts` with: `--strict-markers`, `-ra` (show summary of all except passed), `--cov=cfinterface`, `--cov-fail-under=90`
4. Register markers: `slow` (tests that take > 1s), `benchmark` (performance benchmarks, skipped by default in CI)
5. Set `filterwarnings` to error on DeprecationWarning from cfinterface itself

### Inputs/Props

- File: `/home/rogerio/git/cfinterface/pyproject.toml`

### Outputs/Behavior

Add the following section to pyproject.toml (after the `[tool.hatch.build.targets.wheel]` section, before `[tool.ruff]`):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "-ra",
    "--cov=cfinterface",
    "--cov-fail-under=90",
]
markers = [
    "slow: marks tests as slow (> 1s runtime)",
    "benchmark: performance benchmarks (deselect with -m 'not benchmark')",
]
filterwarnings = [
    "error::DeprecationWarning:cfinterface.*",
]
```

### Error Handling

Not applicable — configuration-only change.

## Acceptance Criteria

- [ ] Given the file `/home/rogerio/git/cfinterface/pyproject.toml`, when searching for `[tool.pytest.ini_options]`, then the section exists with `testpaths`, `addopts`, `markers`, and `filterwarnings` keys
- [ ] Given the updated pyproject.toml, when running `uv run pytest --co -q` from the repository root, then 392 tests are collected without any "PytestUnknownMarkWarning" warnings
- [ ] Given the updated pyproject.toml, when running `uv run pytest -q`, then all 392 tests pass and coverage is reported with a fail-under threshold of 90%
- [ ] Given the updated pyproject.toml, when running `uv run pytest -m benchmark --co -q`, then 0 tests are collected (no benchmark tests exist yet)

## Implementation Guide

### Suggested Approach

1. Open `/home/rogerio/git/cfinterface/pyproject.toml`
2. Add the `[tool.pytest.ini_options]` section after `[tool.hatch.build.targets.wheel]` and before `[tool.ruff]`
3. Verify by running `uv run pytest -q` and confirming no marker warnings appear
4. Verify by running `uv run pytest --co -q` and confirming 392 tests collected

### Key Files to Modify

- `/home/rogerio/git/cfinterface/pyproject.toml`

### Patterns to Follow

- Use TOML array syntax for `addopts` (one flag per line for readability)
- Use TOML array syntax for `markers` (one marker description per line)

### Pitfalls to Avoid

- Do NOT add `--cov-report=xml` to addopts — that is CI-specific and should remain a CLI flag in the workflow
- Do NOT add `--cov-report=term-missing` to addopts — it is verbose for local runs; developers can add it manually
- Do NOT include `-m "not benchmark"` in addopts — that would prevent running benchmarks locally; CI will pass it explicitly
- Do NOT set `minversion` — not needed for this project

## Testing Requirements

### Unit Tests

Not applicable — configuration-only change.

### Integration Tests

- Run `uv run pytest --co -q` and verify 392 tests collected, no warnings
- Run `uv run pytest -q` and verify all tests pass with coverage report
- Run `uv run pytest -m slow --co -q` to verify marker is recognized (0 tests expected)
- Run `uv run pytest -m benchmark --co -q` to verify marker is recognized (0 tests expected)

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None
- **Blocks**: ticket-007-expand-test-matrix (CI uses pytest config), ticket-011-create-conftest-and-fixtures (uses markers), ticket-014-migrate-to-pytest-benchmark (uses benchmark marker)

## Effort Estimate

**Points**: 1
**Confidence**: High
