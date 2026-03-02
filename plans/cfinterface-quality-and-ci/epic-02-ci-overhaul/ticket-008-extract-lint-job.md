# ticket-008 Extract Lint/Quality Job with ty Evaluation

## Context

### Background

The current CI workflow runs mypy, ruff, and sphinx-build as part of every test matrix entry (3 Python versions). This wastes CI minutes since linting results are the same regardless of Python version. After ticket-007 removes these steps from the test job, this ticket creates a dedicated `lint` job that runs once on Python 3.12 with mypy, ruff, ty (informational), and sphinx-build -W.

### Relation to Epic

Second ticket in Epic 2. Creates the lint/quality job that runs static analysis tools independently from the test matrix. Introduces ty as an informational type checker alongside mypy.

### Current State

After ticket-007, the `.github/workflows/main.yml` test job no longer contains mypy, ruff, or sphinx-build steps. Those steps need a new home in a dedicated lint job.

The ty type checker (by Astral, written in Rust) is in beta, targeting 1.0 in 2026. It should be evaluated as a non-blocking step.

## Specification

### Requirements

1. Add a new `lint` job to `.github/workflows/main.yml` that runs on `ubuntu-latest` with Python 3.12
2. The lint job must include the following steps in order:
   a. checkout, install uv, set up Python 3.12, install project
   b. mypy: `uv run mypy ./cfinterface`
   c. ruff: `uv run ruff check ./cfinterface`
   d. ty: `uvx ty check ./cfinterface` with `continue-on-error: true` (informational)
   e. sphinx-build: `uv run python -m sphinx -M html docs/source docs/build -W` (warnings as errors)
3. The lint job should NOT depend on the test job (runs in parallel)
4. The ty step must use `continue-on-error: true` so failures do not block the pipeline
5. Add `ty` as a dev dependency in pyproject.toml so it is available

### Inputs/Props

- File: `/home/rogerio/git/cfinterface/.github/workflows/main.yml`
- File: `/home/rogerio/git/cfinterface/pyproject.toml` (to add ty dev dep)

### Outputs/Behavior

Add the following job to `.github/workflows/main.yml`:

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Set up Python 3.12
      run: uv python install 3.12
    - name: Install the project
      run: |
        uv sync --all-extras --dev
    - name: Type check (mypy)
      run: |
        uv run mypy ./cfinterface
    - name: Lint (ruff)
      run: |
        uv run ruff check ./cfinterface
    - name: Type check (ty - informational)
      continue-on-error: true
      run: |
        uvx ty check ./cfinterface
    - name: Documentation build
      run: |
        uv run python -m sphinx -M html docs/source docs/build -W
```

### Error Handling

- mypy failure blocks the pipeline (strict checking)
- ruff failure blocks the pipeline
- ty failure does NOT block the pipeline (`continue-on-error: true`)
- sphinx-build -W failure blocks the pipeline (warnings are errors)

## Acceptance Criteria

- [ ] Given the file `.github/workflows/main.yml`, when inspecting the `lint` job, then it exists with `runs-on: ubuntu-latest` and `python 3.12` setup
- [ ] Given the file `.github/workflows/main.yml`, when inspecting the `lint` job steps, then it contains steps named "Type check (mypy)", "Lint (ruff)", "Type check (ty - informational)", and "Documentation build"
- [ ] Given the file `.github/workflows/main.yml`, when inspecting the ty step, then `continue-on-error: true` is set
- [ ] Given the file `.github/workflows/main.yml`, when inspecting the sphinx-build command, then it includes the `-W` flag
- [ ] Given the file `.github/workflows/main.yml`, when inspecting the `lint` job, then it does NOT have a `needs: test` dependency (runs in parallel)

## Implementation Guide

### Suggested Approach

1. Open `/home/rogerio/git/cfinterface/.github/workflows/main.yml`
2. Add the `lint` job after the `test` job
3. Use `uv run python -m sphinx` instead of `uv run sphinx-build` (sphinx may not install a CLI entry point in all environments)
4. Add the `-W` flag to sphinx-build to treat warnings as errors
5. Use `uvx ty check` rather than `uv run ty check` — ty is invoked via uvx for isolated execution
6. Validate YAML syntax

### Key Files to Modify

- `/home/rogerio/git/cfinterface/.github/workflows/main.yml`

### Patterns to Follow

- Mirror the checkout/uv/python setup steps from the test job
- Use descriptive step names that clarify tool purpose
- Use `continue-on-error: true` only for informational steps
- Use `-W` flag for sphinx-build to enforce warning-free documentation

### Pitfalls to Avoid

- Do NOT make the lint job depend on the test job (`needs: test`) — they should run in parallel
- Do NOT use `uv run sphinx-build` directly — it may fail if sphinx doesn't install a CLI script; use `uv run python -m sphinx` instead
- Do NOT forget `continue-on-error: true` on the ty step — it is beta and may produce false positives
- Do NOT use `--strict` flag for mypy in the CI command — strict flags are configured in pyproject.toml already
- Ensure the `sphinx -M html` command uses the correct paths: `docs/source` (source) and `docs/build` (output)

## Testing Requirements

### Unit Tests

Not applicable — CI workflow change.

### Integration Tests

- Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('.github/workflows/main.yml'))"`
- Verify the workflow structure is correct by reviewing in GitHub Actions UI after push

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-004-fix-mypy-strict-errors (mypy must pass clean), ticket-005-add-coverage-and-ruff-config (ruff rules must be configured), ticket-007-expand-test-matrix (lint steps removed from test job)
- **Blocks**: None (other tickets do not depend on CI being live)

## Effort Estimate

**Points**: 2
**Confidence**: High
