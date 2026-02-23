# Accumulated Learnings — Epics 01–03

**As of**: 2026-02-23
**Covers**: epic-01-remove-pandas-dependency (tickets 001–004), epic-02-compile-regex-and-storage-enum (tickets 005–009), epic-03-optimize-float-field-write (tickets 010–011)

---

## Codebase Conventions

- `cfinterface/_utils/__init__.py` is the designated home for private, dependency-free internal helpers — add future cross-cutting utilities here
- `cfinterface/storage.py` is the home for storage-type definitions and the `_ensure_storage_type()` deprecation utility — do not scatter storage-related logic into adapter or component files
- Private utilities use one-line or short-paragraph docstrings, not full numpydoc; full numpydoc is reserved for public API classes and methods
- All Field write methods use the guard `self.value is not None and not _is_null(self.value)` — the explicit `is not None` is a documented fast path, do not collapse it
- Optional dependency methods use `try: import X except ImportError: raise ImportError("... pip install cfinterface[X]")` inside the method body — see `cfinterface/files/registerfile.py _as_df()`
- Optional dependency group names match the package name (`pandas`, not `dataframe`) in `pyproject.toml`
- Minor version bumps (not patch) are required whenever the set of packages installed by `pip install cfinterface` changes

## Dependency and Environment

- Test/dev installs must use `pip install -e ".[dev]"` — bare install no longer includes pandas
- pandas lives in both `[pandas]` and `[dev]` optional groups; `[pandas]` is for end users, `[dev]` is for CI and contributors
- Only `numpy` remains a hard runtime dependency as of v1.9.0
- Do not add new dev dependencies without explicit approval; use stdlib alternatives (e.g., `timeit` instead of `pytest-benchmark`)

## Storage Type Pattern

- `StorageType(str, Enum)` with `TEXT = "TEXT"` and `BINARY = "BINARY"` in `cfinterface/storage.py` is the canonical storage sentinel; do NOT use `enum.StrEnum` (Python 3.11+ only)
- All four `factory()` functions use `StorageType` members as dict keys; string lookups work via the `str` mixin hash equality
- All method parameters and class attributes accepting storage values use `Union[str, StorageType]` — never narrow, because 254+ downstream subclasses set `STORAGE = "TEXT"` as a plain string
- The internal `storage=""` default in component method signatures is a sentinel for the TextualRepository fallback — it is NOT deprecated

## Regex Pattern Cache

- Module-level `_pattern_cache: Dict[Union[str, bytes], re.Pattern]` + `_compile(pattern)` helper in `cfinterface/adapters/components/repository.py` replaces all bare `re.search()` calls
- Lazy compilation on first use is correct; cache handles both `str` and `bytes` patterns; no lock needed under CPython GIL

## FloatField Write Optimization (Epic 03)

- The `else` branch in `_textual_write()` (F/f any value, E/e/D/d zero value) now uses at most 3 `str.format()` calls: first at full precision, second at precision reduced by the measured excess, third reduced by 1 more for rounding-carry edge case — see `cfinterface/components/floatfield.py` lines 91-115
- `formatting_format` is computed once before the first format call, not once per iteration; `.replace("E", self.__format)` is applied on all three attempts identically
- Overflow (formatted string longer than field size at `d=0`) is intentionally preserved — `rjust()` does not truncate, so the returned string can exceed `self.size`; do NOT add truncation
- Benchmark shows F fits-at-full-precision: ~0.86 us/write; F precision-reduction: ~1.55 us/write; pre-optimization baseline was ~0.92 us and ~2.30 us respectively

## Benchmark Infrastructure (Epic 03)

- `benchmarks/` directory at repo root contains standalone performance scripts; `benchmarks/__init__.py` is an empty marker making the directory importable
- `benchmarks/bench_floatfield_write.py` is the template for future benchmark scripts: constants `N_WRITES`/`N_REPEATS` at top, `_make_fields()` factory, `_bench_scenario()` timing harness, `run_benchmarks()` orchestrator, `if __name__ == "__main__"` guard
- Smoke tests import `_bench_scenario` and `_make_fields` directly — do NOT import `run_benchmarks()` from tests (it prints to stdout during pytest runs)
- Do NOT put benchmark scripts in `tests/` — `pyproject.toml` testpaths is `tests/` only

## Testing Patterns

- New tests are appended to the existing component test file, not placed in a separate file (confirmed in epics 02 and 03)
- `tests/_utils/` is the location for tests of `cfinterface/_utils/` helpers
- Test files for private internals use in-test state clearing for isolation, not module reloading
- When replacing an algorithm, copy the original as a `_reference_*()` helper in the test file and fuzz-compare the two implementations; this is stronger than testing known outputs alone — see `tests/components/test_floatfield.py` `_reference_textual_write()`
- Fuzz tests that partially skip format branches should use an explicit `continue` with a comment explaining why — see `test_floatfield_write_fuzz_equivalence()`
- Test count: 232 after epic-03 (223 after epic-02 + 9 new)

## Key Files Changed Across All Three Epics

- `cfinterface/_utils/__init__.py` — `_is_null(value: Any) -> bool` using `math.isnan` + `try/except`
- `cfinterface/storage.py` — `StorageType(str, Enum)` enum and `_ensure_storage_type()` deprecation utility
- `cfinterface/adapters/components/repository.py` — `_pattern_cache` dict + `_compile()` helper; `factory()` updated to `Union[str, StorageType]`
- `cfinterface/components/floatfield.py` — `_textual_write()` else-branch replaced with direct 3-attempt computation
- `cfinterface/components/defaultregister.py` — `storage != StorageType.BINARY` guard
- `cfinterface/files/registerfile.py`, `blockfile.py`, `sectionfile.py` — `STORAGE` default `StorageType.TEXT`; `_ensure_storage_type()` in `__init__`
- `cfinterface/__init__.py` — exports `StorageType`; version `1.9.0`
- `pyproject.toml` — pandas in optional-dependencies only
- `benchmarks/__init__.py` — new empty marker file
- `benchmarks/bench_floatfield_write.py` — new standalone benchmark script

## Warnings for Future Epics

- Epic-04 touches `RegisterData`, `BlockData`, `SectionData` containers — no interaction with float formatting; the `_textual_write()` changes are isolated to `floatfield.py`
- Any new DataFrame-export methods must follow the lazy-import pattern in `registerfile.py`, not add a module-level pandas import
- Any new file class using the `STORAGE` class attribute pattern MUST call `_ensure_storage_type(self.__class__.STORAGE)` in its `__init__`
- Epic-05 (type-safe text/binary dispatch) will extend the four `factory()` functions — the current `Union[str, StorageType]` signatures are the correct starting point; do not narrow them before that epic
- Do not create a new `_utils/` submodule unless helper count in `_utils/__init__.py` exceeds three or four functions
- Do not add truncation to `_textual_write()` — overflow (result longer than `self.size`) is a specified behavior that callers of numeric file formats depend on to detect data corruption
