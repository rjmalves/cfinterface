# Master Plan: cfinterface Quality, CI/CD, and Documentation Overhaul

## Executive Summary

After completing a major architecture overhaul (27 tickets, 7 epics) that introduced StorageType, TabularParser, schema versioning, and array-backed data containers, cfinterface v1.9.0 needs hardened project configuration, modernized CI/CD, improved test infrastructure, comprehensive documentation for new features, and a CHANGELOG for the release. This plan addresses all five areas in dependency order.

## Goals & Non-Goals

### Goals

1. **pyproject.toml hardening**: Complete tool configuration (pytest, mypy, coverage, ruff), correct classifiers, py.typed marker
2. **CI/CD overhaul**: Python 3.10-3.14 matrix on Linux, Windows testing (3.12), separate lint job, optional benchmark workflow, ty evaluation
3. **Test infrastructure**: conftest.py with shared fixtures, pytest markers, hypothesis property-based testing, pytest-benchmark integration
4. **Sphinx documentation**: Reference pages for TabularParser, versioning, StorageType, adapters; docstring for read_many(); sphinx-build -W
5. **Release preparation**: CHANGELOG.md for v1.9.0, version classifier updates

### Non-Goals

- macOS CI testing (same POSIX behavior as Linux, no extra signal)
- Full `--strict` mypy (target the three specific flags: disallow_untyped_defs, warn_return_any, strict_optional)
- Fixing all 189 mypy strict errors in this plan (only add config + fix blocking errors)
- Migration from mypy to ty (only evaluation)
- New features or API changes
- Performance optimization work
- Sphinx gallery examples (examples/ directory content)

## Architecture Overview

### Current State

- **pyproject.toml**: Minimal — only ruff line-length=80, no pytest/mypy/coverage config, missing classifiers
- **CI**: Single job on ubuntu-latest with Python 3.10/3.11/3.12, mypy+ruff+sphinx running per Python version
- **Tests**: 392 tests, 94% coverage, no conftest.py, no fixtures, no markers, no hypothesis, one manual timeit benchmark
- **Docs**: Sphinx with RTD theme, autodoc, numpydoc — but NO reference pages for TabularParser, versioning, StorageType, adapters
- **Release**: No CHANGELOG.md, missing classifiers for 3.11-3.14

### Target State

- **pyproject.toml**: Full tool configuration sections for pytest, mypy, coverage, ruff; correct classifiers 3.10-3.14; py.typed marker
- **CI**: Multi-OS matrix (Linux 3.10-3.14, Windows 3.12), separate lint/quality job (mypy+ty+ruff+sphinx), benchmark workflow (manual dispatch)
- **Tests**: conftest.py with shared fixtures, `@pytest.mark.slow`/`@pytest.mark.benchmark` markers, hypothesis strategies for field round-trips, pytest-benchmark for FloatField write
- **Docs**: Complete reference pages for all new features, read_many() docstring, sphinx-build -W in CI
- **Release**: CHANGELOG.md documenting all v1.9.0 changes

### Key Design Decisions

1. **Windows CI single version**: windows-latest with Python 3.12 only — covers line-ending translation behavior without matrix explosion
2. **Python 3.14 support**: Stable since Oct 2025 (3.14.3 current), add to matrix and classifiers
3. **Separate lint job**: mypy/ruff/sphinx-build extracted to dedicated job, runs once on Python 3.12 (not per matrix version)
4. **ty as informational**: Non-blocking CI step alongside mypy — evaluate compatibility, prepare for future migration
5. **Benchmarks via marker**: `@pytest.mark.benchmark` marker with `pytest-benchmark` plugin; default CI skips via `-m "not benchmark"`; optional manual-dispatch workflow runs them
6. **Coverage threshold**: 90% via `--cov-fail-under=90` in pyproject.toml pytest config
7. **Strict mypy flags**: `disallow_untyped_defs`, `warn_return_any`, `strict_optional` — but NOT full `--strict`
8. **Sphinx -W**: Treat warnings as errors to catch broken references in CI

## Technical Approach

### Tech Stack

- Python 3.10+ (numpy>=2.0.0 core dependency)
- pytest + pytest-cov + pytest-benchmark + hypothesis (test infrastructure)
- mypy + ty (type checking)
- ruff (linting)
- Sphinx + RTD theme + numpydoc + autodoc (documentation)
- GitHub Actions (CI/CD)

### Component/Module Breakdown

| Epic | Component                    | Scope                                                                                     |
| ---- | ---------------------------- | ----------------------------------------------------------------------------------------- |
| 1    | pyproject.toml + tool config | Classifiers, pytest config, mypy config, coverage config, ruff expansion, py.typed        |
| 2    | CI workflows                 | main.yml matrix expansion, lint job extraction, benchmark workflow, docs.yml -W flag      |
| 3    | Test infrastructure          | conftest.py, markers, hypothesis strategies, pytest-benchmark migration                   |
| 4    | Sphinx docs                  | Reference pages for TabularParser, versioning, StorageType, adapters, read_many docstring |
| 5    | Release prep                 | CHANGELOG.md, version review                                                              |

### Data Flow

No data flow changes — this plan is entirely about tooling, configuration, documentation, and test infrastructure.

### Testing Strategy

- Each epic's changes are self-verifiable: CI workflows validated by running them, tool configs validated by running the tools, docs validated by sphinx-build -W, tests validated by pytest
- Hypothesis tests will use `@given` with strategies targeting field round-trip correctness
- Benchmark tests gated behind `@pytest.mark.benchmark` marker

## Phases & Milestones

| Phase | Epic                                 | Milestone                                                          | Estimated Duration |
| ----- | ------------------------------------ | ------------------------------------------------------------------ | ------------------ |
| 1     | Epic 1: pyproject.toml + tool config | All tool sections configured, py.typed added, classifiers complete | 3-5 days           |
| 2     | Epic 2: CI overhaul                  | Multi-OS matrix, lint job, benchmark workflow, ty evaluation       | 4-6 days           |
| 3     | Epic 3: Test infrastructure          | conftest.py, markers, hypothesis, pytest-benchmark                 | 5-7 days           |
| 4     | Epic 4: Sphinx docs                  | All new feature reference pages, docstring fixes, -W clean         | 4-6 days           |
| 5     | Epic 5: Release prep                 | CHANGELOG.md complete                                              | 2-3 days           |

## Risk Analysis

| Risk                                                           | Likelihood | Impact          | Mitigation                                                                          |
| -------------------------------------------------------------- | ---------- | --------------- | ----------------------------------------------------------------------------------- |
| mypy strict flags produce too many errors to fix in one ticket | High       | Medium          | Split into config-only ticket (add flags + ignore comments) and gradual fix tickets |
| ty beta produces false positives / incompatible results        | Medium     | Low             | Non-blocking CI step, informational only                                            |
| Python 3.14 incompatibility with numpy or other deps           | Low        | High            | CI matrix will catch it; if broken, exclude from matrix with comment                |
| Windows line-ending differences cause test failures            | Medium     | Medium          | Dedicated ticket to identify and fix platform-specific tests                        |
| hypothesis finds real bugs in field implementations            | Medium     | High (positive) | Good outcome — file issues or fix in separate tickets                               |
| pytest-benchmark conflicts with existing test runner config    | Low        | Low             | pytest-benchmark is a well-maintained pytest plugin with standard integration       |

## Success Metrics

1. All CI checks pass on Linux (3.10-3.14) and Windows (3.12)
2. mypy runs with `disallow_untyped_defs`, `warn_return_any`, `strict_optional` without errors
3. ty runs as informational step (non-blocking)
4. Coverage enforced at >= 90% via fail-under
5. Sphinx builds with `-W` (warnings as errors) without failures
6. All new features (TabularParser, versioning, StorageType, adapters) have reference documentation
7. hypothesis property-based tests cover field round-trips
8. pytest-benchmark replaces manual timeit benchmark
9. CHANGELOG.md documents all v1.9.0 changes
10. py.typed marker present for PEP 561 compliance
