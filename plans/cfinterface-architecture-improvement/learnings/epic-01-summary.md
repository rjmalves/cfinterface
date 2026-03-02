# Accumulated Learnings — Epic 01: Remove pandas Dependency

**As of**: 2026-02-23
**Covers**: epic-01-remove-pandas-dependency (tickets 001-004)

---

## Codebase Conventions

- `cfinterface/_utils/__init__.py` is the designated home for private, dependency-free internal helpers — add future cross-cutting utilities here
- Private utilities use one-line docstrings, not full numpydoc; full numpydoc is reserved for public API classes and methods
- All Field write methods use the guard `self.value is None or _is_null(self.value)` — the explicit `is None` is a documented fast path, do not collapse it
- Optional dependency methods use `try: import X except ImportError: raise ImportError("... pip install cfinterface[X]")` inside the method body — see `registerfile.py _as_df()`
- Optional dependency group names match the package name (`pandas`, not `dataframe`) in `pyproject.toml`
- Minor version bumps (not patch) are required whenever the set of packages installed by `pip install cfinterface` changes

## Dependency and Environment

- Test/dev installs must use `pip install -e ".[dev]"` — bare install no longer includes pandas
- pandas lives in both `[pandas]` and `[dev]` optional groups; `[pandas]` is for end users, `[dev]` is for CI and contributors
- Only `numpy` remains a hard runtime dependency as of v1.9.0

## Testing Patterns

- NaN-write tests are appended to the existing component test file, not placed in a separate file
- `tests/_utils/` is the location for tests of `cfinterface/_utils/` helpers
- All 200 existing tests pass after the epic with zero regressions

## Key Files Changed in This Epic

- `cfinterface/_utils/__init__.py` — new `_is_null(value: Any) -> bool` using `math.isnan` + `try/except`
- `cfinterface/components/floatfield.py`, `integerfield.py`, `literalfield.py`, `datetimefield.py` — removed `import pandas as pd`, added `from cfinterface._utils import _is_null`
- `cfinterface/files/registerfile.py` — lazy pandas import inside `_as_df()`, removed module-level import
- `pyproject.toml` — pandas moved from `dependencies` to `optional-dependencies`
- `cfinterface/__init__.py` — version bumped to `1.9.0`

## Warnings for Future Epics

- Epic 03 rewrites `FloatField._textual_write()` — preserve `self.value is None or _is_null(self.value)` guard unchanged
- Any new DataFrame-export methods on data containers (Epic 04) must follow the lazy-import pattern in `registerfile.py`, not add a module-level pandas import
- Do not create a new `_utils/` submodule unless helper count in `_utils/__init__.py` exceeds three or four functions
