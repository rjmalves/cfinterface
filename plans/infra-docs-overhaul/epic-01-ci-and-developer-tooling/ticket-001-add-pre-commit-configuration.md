# ticket-001 Add pre-commit configuration

## Context

### Background

The cfinterface project enforces code quality via CI (ruff lint, mypy type checking) but has no local pre-commit hooks. Developers must wait for CI feedback to catch lint and type errors. Adding pre-commit hooks creates a fast local feedback loop that catches issues before they reach CI.

### Relation to Epic

This is the first ticket in Epic 01 (CI & Developer Tooling). It establishes the pre-commit infrastructure that other developer-facing improvements build upon.

### Current State

- No `.pre-commit-config.yaml` exists in the repository
- Ruff is configured in `pyproject.toml` at `/home/rogerio/git/cfinterface/pyproject.toml` with rules `["E", "F", "W", "I", "UP", "B", "SIM"]` and `line-length = 80`
- mypy is configured in `pyproject.toml` with `disallow_untyped_defs = true`, `warn_return_any = true`, `strict_optional = true`
- `pre-commit` is not listed in dev dependencies in `pyproject.toml`
- The CI lint job in `.github/workflows/main.yml` runs `ruff check` and `mypy` separately

## Specification

### Requirements

1. Create `.pre-commit-config.yaml` at repository root with three hooks:
   - `ruff` lint check (using `astral-sh/ruff-pre-commit`)
   - `ruff-format` format check (using `astral-sh/ruff-pre-commit`)
   - `mypy` type check (using `pre-commit/mirrors-mypy`) targeting only `cfinterface/` directory
2. Add `pre-commit` to the `dev` optional dependency group in `pyproject.toml`
3. Pin hook versions to current stable releases (ruff v0.9.x, mypy matching the version in dev deps)

### Inputs/Props

- Ruff configuration from `pyproject.toml` `[tool.ruff]` section (hooks will read it automatically)
- mypy configuration from `pyproject.toml` `[tool.mypy]` section

### Outputs/Behavior

- Running `pre-commit run --all-files` passes cleanly on the current codebase
- Running `pre-commit install` sets up git hooks in `.git/hooks/`
- The ruff hook checks lint rules; the ruff-format hook checks formatting; the mypy hook checks types

### Error Handling

- If ruff finds lint issues, the hook fails and prints the violations
- If ruff-format finds unformatted files, the hook fails and auto-formats them (requiring re-stage)
- If mypy finds type errors, the hook fails and prints the errors

## Acceptance Criteria

- [ ] Given the repository root, when `.pre-commit-config.yaml` is read, then it contains exactly three hook entries: `ruff`, `ruff-format`, and `mypy`
- [ ] Given `pyproject.toml`, when the `[project.optional-dependencies].dev` list is read, then it contains `"pre-commit"` as an entry
- [ ] Given a clean checkout with `uv sync --all-extras --dev`, when `pre-commit run --all-files` is executed, then the exit code is 0 and all three hooks report "Passed" or "Skipped"
- [ ] Given `.pre-commit-config.yaml`, when the `ruff` hook entry is inspected, then `repo` is `https://github.com/astral-sh/ruff-pre-commit` and `hooks` includes both `id: ruff` and `id: ruff-format`

## Implementation Guide

### Suggested Approach

1. Create `.pre-commit-config.yaml` at `/home/rogerio/git/cfinterface/.pre-commit-config.yaml`
2. Add the `astral-sh/ruff-pre-commit` repo with two hooks (`ruff` with `--fix` arg, `ruff-format`)
3. Add the `pre-commit/mirrors-mypy` repo with mypy hook, setting `args: [--config-file=pyproject.toml]` and `files: ^cfinterface/` to limit scope
4. Add `additional_dependencies` to the mypy hook for numpy stubs: `["numpy>=2.0.0", "types-setuptools"]`
5. Add `"pre-commit"` to the dev dependencies in `pyproject.toml`
6. Run `uv sync --all-extras --dev` then `pre-commit run --all-files` to verify

### Key Files to Modify

- `/home/rogerio/git/cfinterface/.pre-commit-config.yaml` (CREATE)
- `/home/rogerio/git/cfinterface/pyproject.toml` (MODIFY: add `pre-commit` to dev deps)

### Patterns to Follow

Reference `.pre-commit-config.yaml` structure:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.15.0
    hooks:
      - id: mypy
        files: ^cfinterface/
        args: [--config-file=pyproject.toml]
        additional_dependencies: [...]
```

### Pitfalls to Avoid

- Do NOT add `pre-commit` as a runtime dependency; it belongs in `dev` extras only
- Do NOT set `language_version` on the mypy hook -- let it use the default Python
- Do NOT include test files in the mypy hook scope (the CI lint job already handles that separately)
- The mypy mirror hook runs in its own virtualenv, so `additional_dependencies` must include numpy and any other type stubs that cfinterface imports

## Testing Requirements

### Unit Tests

Not applicable (configuration file, no code changes).

### Integration Tests

- Run `pre-commit run --all-files` and verify exit code 0
- Run `pre-commit run ruff --all-files` and verify it passes
- Run `pre-commit run mypy --all-files` and verify it passes

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
