# ticket-010 Update Docs and Publish Workflows

## Context

### Background

The `docs.yml` workflow builds Sphinx documentation and deploys to gh-pages but does not use the `-W` flag (warnings as errors). The `publish.yml` workflow runs tests and mypy/ruff before building and publishing to PyPI but uses older patterns and does not match the modernized CI conventions established in tickets 007-008. Both workflows need updates for consistency and quality enforcement.

### Relation to Epic

Final ticket in Epic 2. Brings the remaining workflows (docs.yml and publish.yml) in line with the modernized conventions: `-W` flag for sphinx, consistent uv setup patterns, and removal of redundant lint steps from publish (since the lint job in main.yml covers these).

### Current State

**docs.yml** (`/home/rogerio/git/cfinterface/.github/workflows/docs.yml`):

- Runs pytest (redundant with main.yml)
- Uses `uv run sphinx-build -M html docs/source docs/build` without `-W`
- Uses `peaceiris/actions-gh-pages@v3`

**publish.yml** (`/home/rogerio/git/cfinterface/.github/workflows/publish.yml`):

- Runs pytest, mypy, and ruff (redundant — these run in main.yml on every push/PR)
- Uses Python 3.12

## Specification

### Requirements

1. Update `docs.yml`:
   a. Remove the redundant pytest step
   b. Add `-W` flag to sphinx-build command
   c. Use `uv run python -m sphinx` instead of `uv run sphinx-build`
   d. Update `peaceiris/actions-gh-pages` to `@v4`

2. Update `publish.yml`:
   a. Remove redundant mypy and ruff steps (the lint job in main.yml runs on every PR)
   b. Keep pytest step (final safety check before publish)
   c. Add `-m "not benchmark"` to pytest command
   d. Keep the existing build and publish steps unchanged

### Inputs/Props

- File: `/home/rogerio/git/cfinterface/.github/workflows/docs.yml`
- File: `/home/rogerio/git/cfinterface/.github/workflows/publish.yml`

### Outputs/Behavior

Updated `docs.yml`:

```yaml
name: Docs
on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Set up Python
        run: uv python install 3.12
      - name: Install the project
        run: |
          uv sync --all-extras --dev
      - name: Sphinx build
        run: |
          uv run python -m sphinx -M html docs/source docs/build -W
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v4
        if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
        with:
          publish_branch: gh-pages
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/build/html
          force_orphan: true
```

Updated `publish.yml`:

```yaml
name: deploy

on:
  release:
    types: [created]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/cfinterface/
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Set up Python
        run: uv python install 3.12
      - name: Install the project
        run: |
          uv sync --all-extras --dev
      - name: Run tests
        run: |
          uv run pytest -m "not benchmark" ./tests
      - name: Build package
        if: startsWith(github.ref, 'refs/tags')
        run: |
          uv build
      - name: PyPI publish
        if: startsWith(github.ref, 'refs/tags')
        uses: pypa/gh-action-pypi-publish@release/v1
```

### Error Handling

- sphinx-build with `-W` will fail the docs job if any Sphinx warnings exist, which is the desired behavior to catch broken references early

## Acceptance Criteria

- [ ] Given the file `.github/workflows/docs.yml`, when inspecting the sphinx-build command, then it includes the `-W` flag
- [ ] Given the file `.github/workflows/docs.yml`, when inspecting the steps, then no pytest step exists
- [ ] Given the file `.github/workflows/docs.yml`, when inspecting the gh-pages action version, then it uses `@v4`
- [ ] Given the file `.github/workflows/publish.yml`, when inspecting the steps, then no mypy or ruff steps exist
- [ ] Given the file `.github/workflows/publish.yml`, when inspecting the pytest command, then it includes `-m "not benchmark"`

## Implementation Guide

### Suggested Approach

1. Open `/home/rogerio/git/cfinterface/.github/workflows/docs.yml`
2. Remove the pytest step
3. Update sphinx-build to use `uv run python -m sphinx -M html docs/source docs/build -W`
4. Update gh-pages action to `@v4`
5. Open `/home/rogerio/git/cfinterface/.github/workflows/publish.yml`
6. Remove the mypy (`Static typing check`) and ruff (`PEP8 check`) steps
7. Add `-m "not benchmark"` to the pytest command
8. Update step names for consistency (`Run tests`, `Build package`)
9. Validate both YAML files

### Key Files to Modify

- `/home/rogerio/git/cfinterface/.github/workflows/docs.yml`
- `/home/rogerio/git/cfinterface/.github/workflows/publish.yml`

### Patterns to Follow

- Match step naming conventions from the updated main.yml
- Use `uv run python -m sphinx` pattern for sphinx invocation

### Pitfalls to Avoid

- Do NOT remove pytest from publish.yml — it is the final safety check before publishing to PyPI
- Do NOT change the `if: startsWith(github.ref, 'refs/tags')` conditions on build/publish steps
- Do NOT change the PyPI trusted publisher configuration
- Do NOT add `-W` to publish.yml's sphinx step — it does not have a sphinx step (only docs.yml does)
- Ensure `peaceiris/actions-gh-pages@v4` is the correct latest version

## Testing Requirements

### Unit Tests

Not applicable — CI workflow changes.

### Integration Tests

- Validate YAML syntax for both files
- Verify docs.yml workflow runs correctly on next push to main

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-007-expand-test-matrix (establishes the new CI patterns), ticket-008-extract-lint-job (lint steps moved to dedicated job)
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: High
