# Epic 01: CI & Developer Tooling

## Goals

Modernize the CI infrastructure and add local developer tooling to catch quality issues before they reach CI.

## Scope

1. Add `.pre-commit-config.yaml` with ruff (lint + format) and mypy hooks
2. Upgrade all GitHub Actions to latest versions (`setup-uv@v6`, `codecov-action@v5`)
3. Migrate GitHub Pages deployment from `peaceiris/actions-gh-pages` to official `actions/deploy-pages`

## Success Criteria

- `pre-commit run --all-files` passes cleanly on the current codebase
- All four workflow files use latest action versions
- Docs workflow uses `actions/deploy-pages` with proper permissions and artifact upload
- CI continues to pass on all Python versions in the matrix

## Tickets

| ID         | Title                                                   | Effort |
| ---------- | ------------------------------------------------------- | ------ |
| ticket-001 | Add pre-commit configuration                            | 2 pts  |
| ticket-002 | Upgrade GitHub Actions versions                         | 1 pt   |
| ticket-003 | Migrate docs deployment to official GitHub Pages action | 2 pts  |
