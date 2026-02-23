# Accumulated Learnings — Epics 01–02

**As of**: 2026-02-23
**Covers**: epic-01-remove-pandas-dependency (tickets 001–004), epic-02-compile-regex-and-storage-enum (tickets 005–009)

---

## Codebase Conventions

- `cfinterface/_utils/__init__.py` is the designated home for private, dependency-free internal helpers — add future cross-cutting utilities here
- `cfinterface/storage.py` is the home for storage-type definitions and the `_ensure_storage_type()` deprecation utility — do not scatter storage-related logic into adapter or component files
- Private utilities use one-line or short-paragraph docstrings, not full numpydoc; full numpydoc is reserved for public API classes and methods
- All Field write methods use the guard `self.value is None or _is_null(self.value)` — the explicit `is None` is a documented fast path, do not collapse it
- Optional dependency methods use `try: import X except ImportError: raise ImportError("... pip install cfinterface[X]")` inside the method body — see `cfinterface/files/registerfile.py _as_df()`
- Optional dependency group names match the package name (`pandas`, not `dataframe`) in `pyproject.toml`
- Minor version bumps (not patch) are required whenever the set of packages installed by `pip install cfinterface` changes

## Dependency and Environment

- Test/dev installs must use `pip install -e ".[dev]"` — bare install no longer includes pandas
- pandas lives in both `[pandas]` and `[dev]` optional groups; `[pandas]` is for end users, `[dev]` is for CI and contributors
- Only `numpy` remains a hard runtime dependency as of v1.9.0
- `cfinterface/storage.py` imports only `enum` and `warnings` from stdlib — it has zero intra-package dependencies, making it safe to import from any layer without circular import risk

## Storage Type Pattern

- `StorageType(str, Enum)` with `TEXT = "TEXT"` and `BINARY = "BINARY"` in `cfinterface/storage.py` is the canonical storage sentinel; do NOT use `enum.StrEnum` (Python 3.11+ only)
- All four `factory()` functions (`adapters/components/repository.py`, `adapters/components/line/repository.py`, `adapters/reading/repository.py`, `adapters/writing/repository.py`) use `StorageType` members as dict keys; string lookups work transparently via the `str` mixin hash equality
- All method parameters and class attributes that accept storage values use `Union[str, StorageType]` — never narrow to just `StorageType`, because 254+ downstream consumer subclasses set `STORAGE = "TEXT"` as a plain string
- The internal `storage=""` default in component method signatures is a sentinel that triggers the TextualRepository fallback — it is NOT deprecated and must not be warned on; `_ensure_storage_type` explicitly passes `""` through
- Deprecation warnings for string-typed storage values are emitted only at file-class `__init__` time via `_ensure_storage_type(self.__class__.STORAGE)` in `RegisterFile`, `BlockFile`, `SectionFile` — never inside per-line reading loops
- `DefaultRegister` uses `storage != StorageType.BINARY` (not list containment `not in ["BINARY"]`) for the binary-path guard in `cfinterface/components/defaultregister.py`

## Regex Pattern Cache

- Module-level `_pattern_cache: Dict[Union[str, bytes], re.Pattern]` + `_compile(pattern)` helper in `cfinterface/adapters/components/repository.py` replaces all bare `re.search()` calls
- Lazy compilation on first use is correct — Register/Block/Section subclasses defining patterns may not be imported at module load time
- The cache handles both `str` and `bytes` patterns (BinaryRepository uses both types)
- Under the GIL, double-write races in `_compile()` are benign — two threads compiling the same pattern store an equivalent result; no lock is needed for single-process use

## Testing Patterns

- NaN-write tests are appended to the existing component test file, not placed in a separate file
- `tests/_utils/` is the location for tests of `cfinterface/_utils/` helpers
- Test files for private internals (`_compile`, `_pattern_cache`, `_ensure_storage_type`) use in-test clearing (`_pattern_cache.clear()`) for isolation, not module reloading
- All 223 tests pass after epic-02 (200 after epic-01 + 23 new)

## Key Files Changed Across Both Epics

- `cfinterface/_utils/__init__.py` — `_is_null(value: Any) -> bool` using `math.isnan` + `try/except`
- `cfinterface/storage.py` — `StorageType(str, Enum)` enum and `_ensure_storage_type()` deprecation utility (new in epic-02)
- `cfinterface/adapters/components/repository.py` — `_pattern_cache` dict + `_compile()` helper; all 7 `re.search()` calls replaced; `factory()` updated to `Union[str, StorageType]`
- `cfinterface/components/defaultregister.py` — `storage != StorageType.BINARY` replaces list-containment guard
- `cfinterface/files/registerfile.py`, `blockfile.py`, `sectionfile.py` — `STORAGE` default changed to `StorageType.TEXT`; `_ensure_storage_type()` called in `__init__`; lazy pandas import preserved in `_as_df()`
- `cfinterface/__init__.py` — exports `StorageType`; version bumped to `1.9.0`
- `pyproject.toml` — pandas moved from `dependencies` to `optional-dependencies`

## Warnings for Future Epics

- Epic-03 rewrites `FloatField._textual_write()` — preserve `self.value is None or _is_null(self.value)` guard unchanged; FloatField does not touch the storage layer directly
- Any new DataFrame-export methods on data containers (Epic 04) must follow the lazy-import pattern in `registerfile.py`, not add a module-level pandas import
- Any new file class (e.g., a future `TabularFile`) that uses the `STORAGE` class attribute pattern MUST call `_ensure_storage_type(self.__class__.STORAGE)` in its `__init__`
- Epic-05 (type-safe text/binary dispatch) will extend the four `factory()` functions — the current `Union[str, StorageType]` signatures are the correct starting point; do not narrow them before that epic
- Do not create a new `_utils/` submodule unless helper count in `_utils/__init__.py` exceeds three or four functions
