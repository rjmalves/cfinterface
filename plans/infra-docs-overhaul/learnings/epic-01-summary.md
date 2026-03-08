# Epic 01 Learnings: CI & Developer Tooling

## What Was Implemented

1. **Pre-commit configuration** (ticket-001): Added `.pre-commit-config.yaml` with ruff, ruff-format, and mypy hooks. Added `pre-commit` to dev dependencies. Running pre-commit auto-fixed formatting across many source and test files.

2. **GitHub Actions version upgrades** (ticket-002): Bumped `setup-uv@v3` to `@v6` across all 4 workflow files. Bumped `codecov-action@v4` to `@v5`.

3. **Docs deployment migration** (ticket-003): Replaced `peaceiris/actions-gh-pages@v4` with official `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4`. Split single job into build + deploy pattern with proper permissions and concurrency control.

## Key Learnings

- **Pre-commit hooks auto-fix existing code**: When adding ruff-format as a pre-commit hook, expect formatting changes across the entire codebase. The specialist correctly handled this by adding per-file-ignores in `pyproject.toml` for test-specific patterns (B015, E501, F821, SIM117, UP028).

- **Simple version bumps don't need specialist agents**: Tickets like ticket-002 (find-and-replace version strings) are faster to implement directly in the orchestrator than dispatching an agent.

- **GitHub Pages official deployment requires two jobs**: The build job uploads artifacts, the deploy job consumes them. The `if` condition on deploy prevents deployment from `workflow_dispatch` runs on non-main branches.

## Codebase Observations

- `pyproject.toml` is the central configuration hub for ruff, mypy, pytest, and project metadata
- The project has 4 GitHub Actions workflows: main (tests+lint), docs, publish, benchmark
- Documentation uses Sphinx with `docs/source/` as the source directory and `docs/build/` as output
- The project targets Python 3.10-3.14 in its test matrix

## Recommendations for Future Epics

- Epic 02 modifies `docs/source/conf.py` — note that the Sphinx build step in the docs workflow uses `-W` (warnings as errors), so any conf.py changes must not introduce warnings
- The `setup-uv@v6` is now consistent across all workflows, so any new workflow files should use this version
