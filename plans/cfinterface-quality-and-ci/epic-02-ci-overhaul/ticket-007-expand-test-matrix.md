# ticket-007 Expand CI Test Matrix to Python 3.10-3.14 and Windows

## Context

### Background

The current CI workflow (`.github/workflows/main.yml`) runs tests on ubuntu-latest with Python 3.10, 3.11, and 3.12 only. Python 3.13 and 3.14 are missing from the matrix. Windows testing is absent despite the library doing file I/O with text mode, where line-ending translation behaves differently (`\r\n` vs `\n`). This ticket expands the test matrix to cover all supported Python versions and adds Windows CI.

### Relation to Epic

First ticket in Epic 2 (CI overhaul). Expands the test job matrix. The lint job extraction (ticket-008) will modify the same workflow but focuses on the lint/quality steps, not the test matrix.

### Current State

File `.github/workflows/main.yml` (lines 11-16):

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
```

The test job runs pytest, codecov upload, mypy, ruff, and sphinx-build — all in one job per Python version.

## Specification

### Requirements

1. Expand the test matrix to use an `include`-based strategy with:
   - `{os: ubuntu-latest, python-version: "3.10"}`
   - `{os: ubuntu-latest, python-version: "3.11"}`
   - `{os: ubuntu-latest, python-version: "3.12"}`
   - `{os: ubuntu-latest, python-version: "3.13"}`
   - `{os: ubuntu-latest, python-version: "3.14"}`
   - `{os: windows-latest, python-version: "3.12"}`
2. Update `runs-on` to use `${{ matrix.os }}`
3. Remove mypy, ruff, and sphinx-build steps from the test job (they move to the lint job in ticket-008)
4. Add `-m "not benchmark"` to the pytest command to skip benchmark tests (none exist yet, but the marker will be active after Epic 1)
5. Only upload codecov from the ubuntu-latest/3.12 matrix entry (avoid duplicate uploads)
6. Add `fail-fast: false` to the strategy so all matrix entries run even if one fails

### Inputs/Props

- File: `/home/rogerio/git/cfinterface/.github/workflows/main.yml`

### Outputs/Behavior

The test job section of `.github/workflows/main.yml` should become:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            python-version: "3.10"
          - os: ubuntu-latest
            python-version: "3.11"
          - os: ubuntu-latest
            python-version: "3.12"
          - os: ubuntu-latest
            python-version: "3.13"
          - os: ubuntu-latest
            python-version: "3.14"
          - os: windows-latest
            python-version: "3.12"
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}
      - name: Install the project
        run: |
          uv sync --all-extras --dev
      - name: Run tests
        run: |
          uv run pytest -m "not benchmark" --cov-report=xml --cov=cfinterface ./tests
      - name: Upload coverage
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.xml
          flags: unittests
          env_vars: OS,PYTHON
          name: codecov-cfinterface
          fail_ci_if_error: true
          verbose: true
```

### Error Handling

- `fail-fast: false` ensures all matrix entries complete even if one fails
- Windows-specific test failures should be visible in the matrix output

## Acceptance Criteria

- [ ] Given the file `.github/workflows/main.yml`, when inspecting the test job strategy matrix, then it contains 6 entries: 5 ubuntu-latest (3.10-3.14) and 1 windows-latest (3.12)
- [ ] Given the file `.github/workflows/main.yml`, when inspecting the test job, then it does NOT contain mypy, ruff, or sphinx-build steps
- [ ] Given the file `.github/workflows/main.yml`, when inspecting the pytest command, then it includes `-m "not benchmark"`
- [ ] Given the file `.github/workflows/main.yml`, when inspecting the codecov step, then it has an `if` condition restricting it to `ubuntu-latest` and `3.12`
- [ ] Given the file `.github/workflows/main.yml`, when inspecting the strategy, then `fail-fast: false` is set

## Implementation Guide

### Suggested Approach

1. Open `/home/rogerio/git/cfinterface/.github/workflows/main.yml`
2. Replace the `test` job's strategy section with the include-based matrix
3. Update `runs-on` from `ubuntu-latest` to `${{ matrix.os }}`
4. Add `fail-fast: false`
5. Modify the pytest step to include `-m "not benchmark"`
6. Add the `if` condition to the codecov step
7. Remove the mypy, ruff, and sphinx-build steps (they will be added to a new lint job in ticket-008)
8. Validate YAML syntax

### Key Files to Modify

- `/home/rogerio/git/cfinterface/.github/workflows/main.yml`

### Patterns to Follow

- Use `include`-based matrix (not cross-product) for explicit control over OS/Python combinations
- Use `${{ matrix.os }}` for `runs-on`
- Use `if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'` for conditional steps

### Pitfalls to Avoid

- Do NOT use `matrix: {os: [ubuntu-latest, windows-latest], python-version: [...]}` — this creates a cross-product (10 entries) instead of the desired 6
- Do NOT remove the codecov step entirely — only add the condition
- Do NOT add `continue-on-error` to the Windows entry — we want Windows failures to be visible
- Do NOT forget to remove mypy/ruff/sphinx steps — they move to the lint job (ticket-008)
- Ensure `--cov-report=xml` remains in the pytest command (needed for codecov upload)
- Use quotes around Python version strings in YAML to avoid `3.10` being interpreted as `3.1`

## Testing Requirements

### Unit Tests

Not applicable — CI workflow change.

### Integration Tests

- Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('.github/workflows/main.yml'))"`
- Verify the workflow runs correctly by pushing to a branch and checking GitHub Actions output

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-002-add-pytest-configuration (markers must be registered for `-m "not benchmark"` to work)
- **Blocks**: ticket-008-extract-lint-job (lint steps removed from test job here, added to lint job there)

## Effort Estimate

**Points**: 2
**Confidence**: High
