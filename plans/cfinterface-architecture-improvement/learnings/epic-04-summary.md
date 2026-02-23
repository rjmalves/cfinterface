# Accumulated Learnings — Epics 01–04

**As of**: 2026-02-23
**Covers**: epic-01 (tickets 001–004), epic-02 (tickets 005–009), epic-03 (tickets 010–011), epic-04 (tickets 012–016)

---

## Codebase Conventions

- `cfinterface/_utils/__init__.py` is the designated home for private, dependency-free internal helpers — add future cross-cutting utilities here
- `cfinterface/storage.py` is the home for storage-type definitions and `_ensure_storage_type()` — do not scatter storage logic into adapter or component files
- Private utilities use one-line or short-paragraph docstrings; full numpydoc is reserved for public API classes and methods
- All Field write methods use `self.value is not None and not _is_null(self.value)` — the explicit `is not None` is a fast path, do not collapse it
- Optional dependency methods use `try: import X except ImportError: raise ImportError("... pip install cfinterface[X]")` inside the method body — see `cfinterface/files/registerfile.py _as_df()`
- Optional dependency group names match the package name (`pandas`, not `dataframe`) in `pyproject.toml`; minor version bumps required when the installed package set changes

## Dependency and Environment

- Test/dev installs must use `pip install -e ".[dev]"` — bare install no longer includes pandas; only `numpy` is a hard runtime dependency as of v1.9.0
- `cfinterface/storage.py` imports only `enum` and `warnings` — zero intra-package dependencies, safe to import from any layer
- Do not add new dev dependencies without explicit approval; use stdlib alternatives (e.g., `timeit` instead of `pytest-benchmark`)

## Storage Type Pattern

- `StorageType(str, Enum)` with `TEXT = "TEXT"` and `BINARY = "BINARY"` in `cfinterface/storage.py` — do NOT use `enum.StrEnum` (Python 3.11+ only)
- All four `factory()` functions use `StorageType` members as dict keys; all method parameters use `Union[str, StorageType]` — never narrow, because 254+ downstream subclasses set `STORAGE = "TEXT"` as a plain string
- The internal `storage=""` default is a sentinel for the TextualRepository fallback — it is NOT deprecated
- Any new file class using the `STORAGE` attribute pattern MUST call `_ensure_storage_type(self.__class__.STORAGE)` in its `__init__`

## Regex Pattern Cache

- Module-level `_pattern_cache: Dict[Union[str, bytes], re.Pattern]` + `_compile(pattern)` in `cfinterface/adapters/components/repository.py` replaces all bare `re.search()` calls; lazy compilation, handles `str` and `bytes`, no lock needed under CPython GIL

## FloatField Write Optimization and Benchmarks

- `_textual_write()` uses at most 3 `str.format()` calls: full precision, precision minus excess, precision minus one more for rounding-carry — see `cfinterface/components/floatfield.py` lines 91-115; overflow is intentionally preserved, do NOT add truncation
- `benchmarks/` at repo root contains standalone scripts (`benchmarks/__init__.py` is an empty marker); smoke tests import `_bench_scenario` and `_make_fields` directly — do NOT import `run_benchmarks()` from tests; do NOT put benchmark scripts in `tests/`

## Data Container Pattern (Epic 04)

- All three data containers (`RegisterData`, `BlockData`, `SectionData`) use `__slots__ = ["_items", "_type_index"]`: a `list` backing store and a `Dict[Type, List[int]]` secondary index — see `cfinterface/data/registerdata.py` as the canonical reference
- `_index_of(self, item) -> int` uses identity scan (`r is item`), not `list.index()` — `Block.__eq__` and `Section.__eq__` raise `NotImplementedError` on the base class
- `_refresh_indices(start: int)` rewrites `_container` and `_index` on all elements from `start` to end; `append` passes `start = len(_items) - 1` for O(1); all other mutations pass the insertion/removal index
- `_type_index` maps exact `type(item)` keys to index lists; `of_type(t)` matches with `issubclass(key, t)` and calls `indices.sort()` to preserve insertion order; `append` updates in O(1), all other mutations call `_rebuild_type_index()`
- `remove_*_of_type` guards use `is not self._items[0]` (identity), not `!=` — equality raises for base-class `Block` and `Section`

## Component Back-Reference Pattern (Epic 04)

- Each `Register`, `Block`, and `Section` has `_container` (single-underscore, direct reference or `None`) and `_index` (integer) in `__slots__` — single-underscore prevents name mangling so the data container can write `item._container = self` directly
- `previous` and `next` property getters check `_container is not None` first (computed from position); fall back to `__previous_fallback` / `__next_fallback` (double-underscore) for orphaned components; setters always write to fallback slots — see `cfinterface/components/register.py` lines 107-128
- `is_first` and `is_last` follow the same container-first / fallback pattern; on `remove`, set `r._container = None` so the removed element's `previous`/`next` return `None` via the fallback

## Testing Patterns

- New tests are appended to existing test files, not placed in separate files (confirmed across epics 01-04)
- `tests/_utils/` is the location for tests of `cfinterface/_utils/` helpers; private internals use in-test state clearing, not module reloading
- When replacing an algorithm, copy the original as a `_reference_*()` helper and fuzz-compare — see `tests/components/test_floatfield.py`
- Test assertions on computed neighbors use `is` (identity), not `==` — see `tests/data/test_registerdata.py`; `_type_index` is tested directly via `rd._type_index[SomeType]`
- Test count: 268 after epic-04 (232 after epic-03 + 36 new)

## Key Files Changed Across All Four Epics

- `cfinterface/_utils/__init__.py` — `_is_null(value: Any) -> bool`
- `cfinterface/storage.py` — `StorageType(str, Enum)` and `_ensure_storage_type()`
- `cfinterface/adapters/components/repository.py` — `_pattern_cache`, `_compile()`, `Union[str, StorageType]` factory signatures
- `cfinterface/components/floatfield.py` — 3-attempt `_textual_write()` else-branch
- `cfinterface/components/register.py`, `block.py`, `section.py` — computed `previous`/`next`, fallback slots, `_container`/`_index`
- `cfinterface/data/registerdata.py`, `blockdata.py`, `sectiondata.py` — `_items`, `_type_index`, `_refresh_indices`, `_index_of`, `_rebuild_type_index`
- `cfinterface/files/registerfile.py`, `blockfile.py`, `sectionfile.py` — `STORAGE` default, `_ensure_storage_type()`, lazy pandas import
- `cfinterface/__init__.py` — exports `StorageType`; version `1.9.0`; `pyproject.toml` — pandas optional only
- `benchmarks/__init__.py` — empty marker; `benchmarks/bench_floatfield_write.py` — standalone benchmark script

## Warnings for Future Epics

- Epic-05 (type-safe text/binary dispatch) extends the four `factory()` functions — `Union[str, StorageType]` signatures are the correct starting point; do not narrow them before that epic
- Any new data container must follow the `_items` + `_type_index` + `_refresh_indices` + `_index_of` + `_rebuild_type_index` pattern from `cfinterface/data/registerdata.py`
- Any new component class in a container must add `_container`, `_index`, `__previous_fallback`, `__next_fallback` to `__slots__` and implement the computed `previous`/`next`/`is_first`/`is_last` pattern from `cfinterface/components/register.py`
- Epic-06 (generic tabular parser) may introduce new container types — read `cfinterface/data/registerdata.py` in full before designing any new container
- Do NOT add truncation to `_textual_write()`; do NOT add module-level pandas imports; do NOT create a new `_utils/` submodule unless helper count exceeds three or four functions
