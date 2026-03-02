# Accumulated Learnings — Epics 01–05

**As of**: 2026-02-23
**Covers**: epic-01 (tickets 001–004), epic-02 (tickets 005–009), epic-03 (tickets 010–011),
epic-04 (tickets 012–016), epic-05 (tickets 017–020)

---

## Codebase Conventions

- `cfinterface/_utils/__init__.py` -- designated home for private, dependency-free internal helpers
- `cfinterface/storage.py` -- home for `StorageType` and `_ensure_storage_type()`; imports only `enum` and `warnings`; zero intra-package dependencies
- Private utilities use one-line docstrings; full numpydoc is reserved for public API classes
- All Field write methods use `self.value is not None and not _is_null(self.value)` -- explicit `is not None` is a fast path, do not collapse it
- Optional dependency methods use `try: import X except ImportError: raise ImportError("... pip install cfinterface[X]")` inside the method body
- Optional dependency group names match the package name (`pandas`, not `dataframe`) in `pyproject.toml`
- New tests are appended to existing test files, not placed in separate files (confirmed across epics 01-05)
- `tests/_utils/` -- location for tests of `cfinterface/_utils/` helpers

## Dependency and Environment

- Test/dev installs must use `pip install -e ".[dev]"` -- bare install no longer includes pandas; only `numpy` is a hard runtime dependency
- Do not add new dev dependencies without explicit approval; use stdlib alternatives (e.g., `timeit` instead of `pytest-benchmark`)
- Do NOT create a new `_utils/` submodule unless helper count exceeds three or four functions

## Storage Type Pattern

- `StorageType(str, Enum)` with `TEXT = "TEXT"` and `BINARY = "BINARY"` in `cfinterface/storage.py` -- do NOT use `enum.StrEnum` (Python 3.11+ only)
- All four `factory()` functions use `StorageType` members as dict keys; all method parameters use `Union[str, StorageType]` -- never narrow, because 254+ downstream subclasses set `STORAGE = "TEXT"` as a plain string
- The internal `storage=""` default is a sentinel for the TextualRepository fallback -- it is NOT deprecated
- Any new file class using the `STORAGE` attribute pattern MUST call `_ensure_storage_type(self.__class__.STORAGE)` in its `__init__`

## Typing and Overload Conventions (Epic 05)

- Module-level `_T = TypeVar("_T", str, bytes)` in `cfinterface/components/field.py` -- TypeVars used in `@overload` stacks MUST be module-level; class-level TypeVars break the overload mechanism
- `@overload` stub bodies use `...` only -- no docstring, no logic; docstrings live on the implementation method
- For classmethods with overloads: `@classmethod` before `@overload` in each stub; implementation carries only `@classmethod` -- see `cfinterface/components/register.py` and `cfinterface/components/block.py`
- Three-overload `factory()` pattern: `Literal["TEXT"] -> Type[TextualRepository]`, `Literal["BINARY"] -> Type[BinaryRepository]`, `Union[str, StorageType] -> Type[Repository]` (fallback) -- the fallback overload is required for runtime-value call sites; see all four adapter modules
- `Literal["TEXT"]` covers both `StorageType.TEXT` and the plain string `"TEXT"` because `StorageType(str, Enum)` -- no separate enum-member overload needed
- Abstract `Repository` base class retains `Union[str, bytes]` in all signatures; only concrete `TextualRepository` / `BinaryRepository` narrow to `str` or `bytes` -- narrowing the base would break polymorphic callers
- `Line.write()` return type is permanently `Union[str, bytes]` -- cannot be overloaded because the discriminator is the constructor `storage` argument, not any argument to `write()` itself
- `Line` must NOT be made generic (`Line[str]`) -- 254+ downstream subclasses set class-level `LINE = Line(fields)` without a type argument; making it generic is a breaking change
- `# type: ignore` retained in `cfinterface/adapters/components/line/repository.py` on `field.read(line)` in `BinaryRepository.read()` -- mypy cannot prove narrowing through the `Field.read()` overload in that context

## Regex Pattern Cache

- Module-level `_pattern_cache: Dict[Union[str, bytes], re.Pattern]` + `_compile(pattern)` in `cfinterface/adapters/components/repository.py` -- lazy compilation, handles `str` and `bytes`, reusable for any new pattern-matching logic

## FloatField Write Optimization

- `_textual_write()` uses at most 3 `str.format()` calls: full precision, precision minus excess, precision minus one more for rounding-carry -- see `cfinterface/components/floatfield.py`; overflow is intentionally preserved, do NOT add truncation
- `benchmarks/` at repo root contains standalone scripts; smoke tests import `_bench_scenario` and `_make_fields` directly -- do NOT import `run_benchmarks()` from tests

## Data Container Pattern (Epic 04)

- All three data containers (`RegisterData`, `BlockData`, `SectionData`) use `__slots__ = ["_items", "_type_index"]` -- `cfinterface/data/registerdata.py` is the canonical reference
- `_index_of(self, item) -> int` uses identity scan (`r is item`), not `list.index()` -- `Block.__eq__` and `Section.__eq__` raise `NotImplementedError` on the base class
- `_refresh_indices(start: int)` rewrites `_container` and `_index` on all elements from `start` to end; `append` passes `start = len(_items) - 1` for O(1)
- `_type_index` maps exact `type(item)` keys; `of_type(t)` matches with `issubclass(key, t)` and calls `indices.sort()` to preserve insertion order
- `remove_*_of_type` guards use `is not self._items[0]` (identity), not `!=`

## Component Back-Reference Pattern (Epic 04)

- Each `Register`, `Block`, `Section` has `_container` (single-underscore) and `_index` (integer) in `__slots__` -- single-underscore prevents name mangling so the data container can write `item._container = self` directly
- `previous` and `next` property getters check `_container is not None` first; fall back to `__previous_fallback` / `__next_fallback` (double-underscore) for orphaned components
- `is_first` and `is_last` follow the same container-first / fallback pattern; on `remove`, set `r._container = None`

## Testing Patterns

- Test assertions on computed neighbors use `is` (identity), not `==` -- see `tests/data/test_registerdata.py`
- When replacing an algorithm, copy the original as a `_reference_*()` helper and fuzz-compare -- see `tests/components/test_floatfield.py`
- Test count: 292 after epic-05 (268 after epic-04 + 24 new)

## Key Files Reference

- `cfinterface/_utils/__init__.py` -- `_is_null(value: Any) -> bool`
- `cfinterface/storage.py` -- `StorageType(str, Enum)` and `_ensure_storage_type()`
- `cfinterface/components/field.py` -- module-level `_T`, `@overload` on `read()`/`write()`, simplified write body
- `cfinterface/components/line.py` -- `@overload` on `read()` only; `write()` stays `Union[str, bytes]`
- `cfinterface/components/register.py` -- `@overload` on `matches()`; `_container`/`_index`/fallback slots
- `cfinterface/components/block.py` -- `@overload` on `begins()`/`ends()`; same back-reference slots
- `cfinterface/adapters/components/repository.py` -- `_pattern_cache`, `_compile()`, three-overload `factory()`, narrowed concrete types
- `cfinterface/adapters/components/line/repository.py` -- three-overload `factory()`, narrowed concrete types, `# type: ignore` on binary field read
- `cfinterface/adapters/reading/repository.py` -- three-overload `factory()`, `BinaryIO`/`TextIO` filepointer types
- `cfinterface/adapters/writing/repository.py` -- three-overload `factory()`, `isinstance` guards retained for safety
- `cfinterface/components/floatfield.py` -- 3-attempt `_textual_write()` else-branch
- `cfinterface/data/registerdata.py`, `blockdata.py`, `sectiondata.py` -- `_items`, `_type_index`, `_refresh_indices`, `_index_of`, `_rebuild_type_index`

## Warnings for Future Epics

- Epic-06 tabular parser: do NOT make `Line` or any new parser class generic -- use `storage: Union[str, StorageType]` constructor argument instead; compose from `cfinterface/adapters/components/line/repository.py` `TextualRepository` for delimiter reading; apply three-overload `factory()` pattern for any new factory function
- Epic-06 tabular parser: `_compile()` / `_pattern_cache` from `cfinterface/adapters/components/repository.py` is available for reuse in any new pattern-matching logic
- Epic-07 schema versioning: `storage: Union[str, StorageType]` parameter threading is load-bearing and must not be narrowed in any method signature; `Literal["v1"]`/`Literal["v2"]` overloads on schema-version factory functions would work with the same three-overload pattern
- Any new data container must follow the `_items` + `_type_index` + `_refresh_indices` + `_index_of` + `_rebuild_type_index` pattern from `cfinterface/data/registerdata.py`
- Any new component class in a container must add `_container`, `_index`, `__previous_fallback`, `__next_fallback` to `__slots__` and implement the computed `previous`/`next`/`is_first`/`is_last` pattern from `cfinterface/components/register.py`
- Do NOT add truncation to `_textual_write()`; do NOT add module-level pandas imports
