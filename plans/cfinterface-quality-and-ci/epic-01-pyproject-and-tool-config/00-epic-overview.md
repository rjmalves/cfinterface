# Epic 01: pyproject.toml Hardening and Tool Configuration

## Goal

Transform pyproject.toml from a minimal build-only configuration into a fully hardened project manifest with complete tool configuration sections, correct Python classifiers, PEP 561 compliance, and expanded dev dependencies.

## Scope

- Add missing Python version classifiers (3.11, 3.12, 3.13, 3.14)
- Add `[tool.pytest.ini_options]` section with markers, coverage config, and default flags
- Add `[tool.mypy]` section with strict flags (disallow_untyped_defs, warn_return_any, strict_optional)
- Add `[tool.coverage]` section with source, omit, and fail-under settings
- Expand `[tool.ruff]` with select rules, per-file-ignores, and target-version
- Add py.typed marker file for PEP 561 compliance
- Add hypothesis, pytest-benchmark, and pandas-stubs to dev dependencies
- Fix mypy errors introduced by strict flags (add type annotations to untyped functions)

## Out of Scope

- CI workflow changes (Epic 2)
- New test files (Epic 3)
- Documentation changes (Epic 4)
- Full `--strict` mypy compliance (only the three specified flags)

## Dependencies

- None (this is the foundation epic)

## Tickets

1. **ticket-001-update-classifiers-and-metadata** — Add missing Python version classifiers and update development status
2. **ticket-002-add-pytest-configuration** — Add [tool.pytest.ini_options] with markers, default flags, and coverage integration
3. **ticket-003-add-mypy-configuration** — Add [tool.mypy] with strict flags and per-module overrides
4. **ticket-004-fix-mypy-strict-errors** — Add type annotations to all untyped functions to pass strict mypy
5. **ticket-005-add-coverage-and-ruff-config** — Add [tool.coverage] section and expand [tool.ruff] rules
6. **ticket-006-add-py-typed-and-dev-deps** — Add py.typed marker and new dev dependencies (hypothesis, pytest-benchmark, pandas-stubs)

## Success Criteria

- `uv run mypy ./cfinterface` passes with disallow_untyped_defs, warn_return_any, strict_optional
- `uv run pytest` recognizes custom markers without warnings
- `uv run ruff check ./cfinterface` passes with expanded rule set
- py.typed marker exists at `cfinterface/py.typed`
- All classifiers 3.10-3.14 present in pyproject.toml
