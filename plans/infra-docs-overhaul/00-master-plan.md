# Master Plan: Infrastructure & Documentation Overhaul

## Executive Summary

This plan modernizes cfinterface's developer tooling, CI infrastructure, and documentation to match the standards established in sibling projects (sintetizador-newave). The work addresses gaps in pre-commit hooks, GitHub Pages deployment, Sphinx theme, documentation content, and repository polish -- while preserving the strong foundation already in place (OIDC publishing, test matrix, CHANGELOG, README).

## Goals & Non-Goals

### Goals

- Migrate Sphinx theme from RTD to Furo (dark mode, mobile, maintained)
- Add pre-commit hooks (ruff + mypy) as local enforcement point
- Migrate GitHub Pages deployment to official `actions/deploy-pages`
- Upgrade all GitHub Actions to latest versions (`setup-uv@v6`)
- Create architecture overview, FAQ, migration guide, and performance tips in pt-BR
- Fix contributing documentation (wrong repo URL, outdated instructions)
- Create root-level CONTRIBUTING.md
- Expand examples gallery

### Non-Goals

- Changing the CHANGELOG format (already follows Keep a Changelog)
- Modifying PyPI trusted publishing (already uses OIDC)
- Changing the README structure (already has badges, quickstart, features)
- Adding new CI jobs or changing the test matrix
- Modifying any library source code in `cfinterface/`

## Architecture Overview

### Current State

- **CI**: GitHub Actions with `setup-uv@v3`, `peaceiris/actions-gh-pages@v4` for docs
- **Docs**: Sphinx with `sphinx-rtd-theme`, language set to `en_US`, 3 sphinx-gallery examples
- **Pre-commit**: None
- **Contributing**: Only `docs/source/getting_started/contributing.rst` with incorrect clone URL pointing to `inewave` instead of `cfinterface`
- **Docs content**: API reference and tutorial exist; no architecture overview, FAQ, migration guide, or performance tips

### Target State

- **CI**: GitHub Actions with `setup-uv@v6`, official `actions/deploy-pages` for docs
- **Docs**: Sphinx with Furo theme, language set to `pt-BR`, 5+ sphinx-gallery examples
- **Pre-commit**: `.pre-commit-config.yaml` with ruff, ruff-format, and mypy hooks
- **Contributing**: Root `CONTRIBUTING.md` + updated `contributing.rst` in docs
- **Docs content**: Architecture overview, FAQ, migration guide from v1.8 to v1.9, performance tips, all in pt-BR

### Key Design Decisions

1. **Furo over RTD theme**: Better dark mode support, mobile responsiveness, active maintenance, consistent with sintetizador-newave
2. **Pre-commit as enforcement**: Catches issues before CI, reduces feedback loop
3. **Official GitHub Pages action**: `actions/deploy-pages` is the GitHub-recommended path, replaces third-party `peaceiris/actions-gh-pages`
4. **pt-BR documentation**: Downstream audience is Brazilian Portuguese-speaking
5. **Text-based diagrams**: No external Sphinx extensions for diagrams; use code blocks or ASCII art

## Technical Approach

### Tech Stack

- Python (Sphinx, pre-commit)
- GitHub Actions (YAML workflows)
- reStructuredText (documentation content)

### Component/Module Breakdown

| Component       | Scope                                                                                         |
| --------------- | --------------------------------------------------------------------------------------------- |
| CI workflows    | `.github/workflows/docs.yml`, `.github/workflows/main.yml`, `.github/workflows/benchmark.yml` |
| Pre-commit      | `.pre-commit-config.yaml`, `pyproject.toml`                                                   |
| Sphinx config   | `docs/source/conf.py`, `pyproject.toml`                                                       |
| Docs content    | `docs/source/` RST files                                                                      |
| Examples        | `examples/*.py`                                                                               |
| Repo root files | `CONTRIBUTING.md`                                                                             |

### Data Flow

No data flow changes. This plan affects developer tooling and documentation only.

### Testing Strategy

- **CI workflows**: Verified by successful GitHub Actions runs
- **Pre-commit**: Verified by running `pre-commit run --all-files` locally
- **Sphinx build**: Verified by `sphinx-build -W` (warnings-as-errors) passing
- **Documentation content**: Verified by Sphinx build + visual review

## Phases & Milestones

| Epic | Name                   | Tickets | Focus                                                                              |
| ---- | ---------------------- | ------- | ---------------------------------------------------------------------------------- |
| 1    | CI & Developer Tooling | 3       | Pre-commit hooks, GitHub Actions upgrades, docs deployment migration               |
| 2    | Sphinx Modernization   | 3       | Furo theme migration, conf.py pt-BR, example expansion                             |
| 3    | Documentation Content  | 5       | Architecture overview, FAQ, migration guide, performance tips, contributing update |
| 4    | Repository Polish      | 2       | Root CONTRIBUTING.md, contributing.rst fix                                         |

## Risk Analysis

| Risk                                      | Likelihood | Impact | Mitigation                                                                               |
| ----------------------------------------- | ---------- | ------ | ---------------------------------------------------------------------------------------- |
| Furo theme breaks existing CSS/templates  | Low        | Medium | Furo is well-tested; remove RTD-specific options from conf.py                            |
| GitHub Pages migration causes docs outage | Low        | High   | Test with a manual workflow_dispatch trigger before merging                              |
| pre-commit mypy hook is too slow          | Medium     | Low    | Configure mypy hook with `--install-types --non-interactive` and limit to `cfinterface/` |

## Success Metrics

- All CI workflows pass with upgraded actions
- `pre-commit run --all-files` passes cleanly
- Sphinx build with Furo produces working documentation site
- All new documentation pages render correctly in pt-BR
- Contributing documentation references correct repository
