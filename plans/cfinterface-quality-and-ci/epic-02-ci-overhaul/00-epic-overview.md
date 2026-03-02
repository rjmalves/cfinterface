# Epic 02: CI/CD Pipeline Overhaul

## Goal

Modernize the GitHub Actions CI/CD pipeline with expanded Python version matrix, Windows testing, separated lint/quality job, optional benchmark workflow, ty type checker evaluation, and Sphinx -W enforcement.

## Scope

- Expand main.yml Python matrix to 3.10, 3.11, 3.12, 3.13, 3.14 on ubuntu-latest
- Add Windows testing (windows-latest, Python 3.12)
- Extract mypy/ruff/sphinx into a separate lint/quality job (runs once, not per Python version)
- Add ty as informational (continue-on-error) step in lint job
- Add `sphinx-build -W` flag in both main.yml lint job and docs.yml
- Create optional manual-dispatch benchmark workflow
- Update docs.yml and publish.yml to match new conventions

## Out of Scope

- macOS CI testing
- Changing test content (Epic 3)
- Documentation page content (Epic 4)
- pyproject.toml tool config (Epic 1, must be done first)

## Dependencies

- **Epic 1** must be completed first (mypy config, pytest markers, ruff config all referenced by CI)

## Tickets

1. **ticket-007-expand-test-matrix** — Expand main.yml test job to Python 3.10-3.14 on Linux + 3.12 on Windows
2. **ticket-008-extract-lint-job** — Extract mypy/ruff/sphinx into dedicated lint job with ty evaluation
3. **ticket-009-create-benchmark-workflow** — Create manual-dispatch benchmark workflow using pytest-benchmark
4. **ticket-010-update-docs-and-publish-workflows** — Update docs.yml with -W flag and publish.yml with modern patterns

## Success Criteria

- CI test job runs on 6 matrix entries (5 Linux + 1 Windows)
- Lint job runs once on Python 3.12 with mypy, ruff, ty (informational), sphinx -W
- Benchmark workflow exists and is manually triggerable
- docs.yml builds with `-W` flag
- publish.yml uses consistent uv + Python patterns
