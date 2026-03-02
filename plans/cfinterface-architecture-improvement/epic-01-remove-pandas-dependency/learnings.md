# Epic 01 Learnings: Remove pandas Dependency from Core

**Epic**: epic-01-remove-pandas-dependency
**Completed**: 2026-02-23
**Tickets**: 4 (all completed)
**Tests**: 200 passing (0 regressions)

---

## Patterns Established

**Private utility module at `cfinterface/_utils/__init__.py`**
The `_utils` package now serves as the home for shared internal helpers that must not import heavy third-party libraries. The `_is_null()` function is the first resident. Future epics should place similar cross-cutting, dependency-free utilities here rather than inlining them in component files or reaching for external packages.

**Lazy import pattern for optional dependencies**
`cfinterface/files/registerfile.py` demonstrates the standard pattern for optional dependencies: `try: import X except ImportError: raise ImportError("... pip install cfinterface[X]")` inside the method body, not at module level. This pattern should be used verbatim for any future method that needs an optional library (e.g., matplotlib, plotly).

**Redundant guard preserved intentionally**
All four Field subclasses keep the pattern `self.value is None or _is_null(self.value)` rather than collapsing it to just `_is_null(self.value)`, even though `_is_null` handles `None`. The explicit `is None` short-circuit is a documented intentional fast path. This convention should be preserved in any future refactoring of write methods.

**Optional dependency group named after the package**
`pyproject.toml` names the optional group `pandas` (not `dataframe` or `optional`), so consumers install with `pip install cfinterface[pandas]`. This naming convention should be followed for any future optional groups (e.g., `cfinterface[matplotlib]`).

---

## Architectural Decisions

**`math.isnan()` with `try/except` instead of `pd.isnull()`**
Decision: use `math.isnan(value)` wrapped in `try/except (TypeError, ValueError)`.
Rejected alternatives: `value != value` (works but confusing, fragile with custom `__eq__`), importing numpy's `isnan` (adds numpy as a hard call dependency inside utils), calling `pd.isnull` (defeats the purpose).
Rationale: `math.isnan()` handles Python `float` and all numpy scalar types because numpy scalars implement `__float__`. The `try/except` cleanly covers non-numeric types (strings, datetimes) without isinstance chains. This is in `cfinterface/_utils/__init__.py`.

**Docstring reduced from full numpydoc to one-line summary**
Decision: `_is_null()` was implemented with a one-line docstring ("Return True if value is None or NaN.") rather than the full numpydoc format specified in the ticket's suggested code.
Rejected: full numpydoc with `:param:`, `:type:`, `:return:`, `:rtype:` sections.
Rationale: the function is a private internal utility (underscore prefix); the abbreviated form is consistent with how other private helpers in the codebase are documented. Future private utilities in `_utils` should follow the same abbreviated style.

**pandas moved to both `pandas` and `dev` optional groups**
Decision: add pandas to a new `[project.optional-dependencies]` group named `pandas`, AND add it to the existing `dev` group.
Rejected: removing pandas from `dev` (tests for `_as_df()` require pandas; removing it would break CI).
Rationale: consumers who need DataFrame support install `cfinterface[pandas]`; developers and CI install `cfinterface[dev]` and get pandas automatically. This is reflected in `pyproject.toml`.

---

## Files and Structures Created

- `cfinterface/_utils/__init__.py` - Private utility module. Currently contains only `_is_null(value: Any) -> bool`. This is the designated location for future internal helpers that must avoid heavy runtime imports.
- `tests/_utils/__init__.py` - Test package for utilities.
- `tests/_utils/test_is_null.py` - 13 unit tests covering None, float NaN, numpy NaN variants, zero, integers, strings, datetimes, and numpy scalars.

---

## Conventions Adopted

**Import location for `_is_null` in Field subclasses**
Each file imports as `from cfinterface._utils import _is_null` at the top of the file alongside other internal imports, not inline. See `cfinterface/components/floatfield.py`, `integerfield.py`, `literalfield.py`, `datetimefield.py`.

**NaN write tests placed at the bottom of existing component test files**
NaN-write tests were appended to `tests/components/test_floatfield.py` and `tests/components/test_integerfield.py` rather than placed in a separate file. This keeps all behavioral tests for a given component together.

**Version bump on dependency scope change**
Moving pandas from required to optional triggered a minor version bump: `1.8.3` -> `1.9.0` in `cfinterface/__init__.py`. This establishes the convention that any change affecting what `pip install cfinterface` installs is a minor version increment (not a patch).

---

## Surprises and Deviations

**`_as_df()` already had no return type annotation**
The ticket's implementation guide warned "the method already has no return type annotation" and said to avoid adding one. This was confirmed: `registerfile.py` `_as_df()` has only a docstring `:rtype: pd.DataFrame` but no Python return annotation. The lazy import pattern was applied without adding a type annotation, keeping the existing convention.

**`math` module imported in test file but not used directly**
`tests/_utils/test_is_null.py` imports `math` at the top but does not call any `math` function in the tests. This is a minor lint issue left in the committed code. Future test files for `_utils` should avoid unused imports.

**`RegisterFile._as_df()` uses `list()` wrapping of generator**
The implemented code in `registerfile.py` line 59 is `registers = list(self.data.of_type(register_type))`, while the original code and the ticket's suggested implementation used a list comprehension `[b for b in self.data.of_type(register_type)]`. Both are equivalent; the `list()` call is slightly more idiomatic when the source is already an iterable. No functional difference.

---

## Recommendations for Future Epics

**Epic 02 (compile regex + StorageType enum) should add utilities to `_utils` if needed**
The `_utils` package is now established. If regex compilation introduces shared helpers (e.g., a `_compile_pattern()` cache wrapper), place them in `cfinterface/_utils/__init__.py` alongside `_is_null`. Do not create a new `_utils/regex.py` module unless the helper count exceeds three or four functions.

**Epic 04 (array-backed data containers) should not introduce pandas in new APIs**
The `_as_df()` lazy-import pattern is now the approved way to expose DataFrame functionality. Any new container-level DataFrame export methods (e.g., on `BlockData` or `SectionData`) should follow exactly the same `try/except ImportError` pattern shown in `cfinterface/files/registerfile.py`.

**The `_is_null` guard pattern should survive FloatField refactoring in Epic 03**
Epic 03 will rewrite `FloatField._textual_write()`. The `self.value is None or _is_null(self.value)` guard at line 67 of `cfinterface/components/floatfield.py` must be preserved verbatim in the rewritten method. Do not collapse it to `_is_null(self.value)` even though `_is_null` handles `None`.

**Test environment setup: always use `cfinterface[dev]` not bare install**
CI and local test runs must install with `pip install -e ".[dev]"` to get pandas. A bare `pip install -e .` will no longer have pandas and any test touching `_as_df()` will raise `ImportError`. This is correct behavior but must be documented in contributor setup instructions.
