# ticket-005 Add Coverage and Expanded Ruff Configuration

## Context

### Background

cfinterface's pyproject.toml has only `line-length = 80` under `[tool.ruff]` — no rule selection, no target-version, no per-file-ignores. There is also no `[tool.coverage]` section, meaning coverage source/omit settings are purely CLI-driven. This ticket adds proper coverage configuration and expands ruff rules to enforce a consistent code style.

### Relation to Epic

Fifth ticket in Epic 1. Completes the tool configuration sections in pyproject.toml. The coverage config will be used by CI (Epic 2) and the ruff config ensures consistent linting.

### Current State

- `/home/rogerio/git/cfinterface/pyproject.toml` `[tool.ruff]` section contains only: `line-length = 80`
- No `[tool.coverage.run]` or `[tool.coverage.report]` sections exist
- `uv run ruff check ./cfinterface` passes with current minimal config
- Coverage is ~94% as reported by `pytest --cov=cfinterface`

## Specification

### Requirements

1. Add `[tool.coverage.run]` with `source = ["cfinterface"]` and `omit = ["cfinterface/__pycache__/*"]`
2. Add `[tool.coverage.report]` with `fail_under = 90`, `show_missing = true`, `exclude_lines` for standard patterns (`pragma: no cover`, `if __name__`, `if TYPE_CHECKING`)
3. Expand `[tool.ruff]` with `target-version = "py310"`
4. Add `[tool.ruff.lint]` with `select` rules: `E` (pycodestyle errors), `F` (pyflakes), `W` (pycodestyle warnings), `I` (isort), `UP` (pyupgrade), `B` (bugbear), `SIM` (simplify)
5. Add `[tool.ruff.lint.per-file-ignores]` for test files: `"tests/**/*.py" = ["B011", "S101"]` (assert usage is normal in tests)
6. Add `[tool.ruff.lint.isort]` with `known-first-party = ["cfinterface"]`

### Inputs/Props

- File: `/home/rogerio/git/cfinterface/pyproject.toml`

### Outputs/Behavior

Replace the existing `[tool.ruff]` section and add coverage sections:

```toml
[tool.coverage.run]
source = ["cfinterface"]
omit = ["cfinterface/__pycache__/*"]

[tool.coverage.report]
fail_under = 90
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__",
    "if TYPE_CHECKING",
]

[tool.ruff]
line-length = 80
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["B011", "S101"]

[tool.ruff.lint.isort]
known-first-party = ["cfinterface"]
```

### Error Handling

- If the new ruff rules surface existing violations, they must be fixed in the cfinterface source files as part of this ticket (the fix scope is limited to whatever violations the expanded rules catch — expected to be few or zero based on the already-clean codebase)

## Acceptance Criteria

- [ ] Given the file `/home/rogerio/git/cfinterface/pyproject.toml`, when searching for `[tool.coverage.run]`, then the section exists with `source = ["cfinterface"]`
- [ ] Given the file `/home/rogerio/git/cfinterface/pyproject.toml`, when searching for `[tool.coverage.report]`, then the section exists with `fail_under = 90`
- [ ] Given the file `/home/rogerio/git/cfinterface/pyproject.toml`, when searching for `[tool.ruff.lint]`, then the section exists with `select = ["E", "F", "W", "I", "UP", "B", "SIM"]`
- [ ] Given the updated pyproject.toml, when running `uv run ruff check ./cfinterface`, then ruff exits with return code 0
- [ ] Given the updated pyproject.toml, when running `uv run pytest -q`, then all 392 tests pass and coverage reports with fail-under=90

## Implementation Guide

### Suggested Approach

1. Open `/home/rogerio/git/cfinterface/pyproject.toml`
2. Add `[tool.coverage.run]` and `[tool.coverage.report]` sections after the mypy section
3. Replace the existing `[tool.ruff]` section with the expanded version (keep it at the end of the file)
4. Run `uv run ruff check ./cfinterface` to check for new violations
5. If violations exist, fix them (expected: few or none, since the codebase already passes basic ruff)
6. Run `uv run pytest -q` to confirm tests still pass

### Key Files to Modify

- `/home/rogerio/git/cfinterface/pyproject.toml`
- Any cfinterface source files with new ruff violations (if any)

### Patterns to Follow

- Keep TOML sections in a logical order: build-system, project, hatch, pytest, mypy, coverage, ruff
- Use TOML array syntax for multi-value settings

### Pitfalls to Avoid

- Do NOT add `S` (bandit) rules beyond test-specific ignores — bandit is noisy for library code and not requested
- Do NOT add `D` (pydocstyle) rules — docstring enforcement is not requested and would create hundreds of violations
- Do NOT set `fix = true` in ruff config — auto-fixing should be opt-in via CLI
- Do NOT change `line-length = 80` — it is already set and correct
- If `UP` (pyupgrade) suggests removing `Union` or `Optional` in favor of `X | Y` syntax, ensure the minimum Python version (3.10) supports it (it does for runtime, but `from __future__ import annotations` may be needed for some cases)

## Testing Requirements

### Unit Tests

Not applicable — configuration-only change (plus possible minor source fixes).

### Integration Tests

- Run `uv run ruff check ./cfinterface` — must pass with 0 violations
- Run `uv run pytest -q` — all 392 tests pass, coverage >= 90%

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None (independent of other tickets, but logically follows ticket-003/004)
- **Blocks**: ticket-008-extract-lint-job (CI lint job runs ruff with these rules)

## Effort Estimate

**Points**: 2
**Confidence**: High
