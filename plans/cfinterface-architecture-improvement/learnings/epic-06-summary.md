# Accumulated Learnings — Epics 01–06

**As of**: 2026-02-23
**Covers**: epic-01 (tickets 001–004), epic-02 (tickets 005–009), epic-03 (tickets 010–011),
epic-04 (tickets 012–016), epic-05 (tickets 017–020), epic-06 (tickets 021–023)

---

## Codebase Conventions

- `cfinterface/_utils/__init__.py` -- designated home for private, dependency-free internal helpers
- `cfinterface/storage.py` -- home for `StorageType` and `_ensure_storage_type()`; imports only `enum` and `warnings`; zero intra-package dependencies
- Private utilities use one-line docstrings; full numpydoc is reserved for public API classes
- All Field write methods use `self.value is not None and not _is_null(self.value)` -- explicit `is not None` is a fast path, do not collapse it
- Optional dependency methods use `try: import X except ImportError: raise ImportError("... pip install cfinterface[X]")` inside the method body
- Optional dependency group names match the package name (`pandas`, not `dataframe`) in `pyproject.toml`
- New tests are appended to existing test files, not placed in separate files (confirmed across epics 01-06)
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
- Abstract `Repository` base class retains `Union[str, bytes]` in all signatures; only concrete `TextualRepository` / `BinaryRepository` narrow to `str` or `bytes`
- `Line.write()` return type is permanently `Union[str, bytes]` -- cannot be overloaded because the discriminator is the constructor `storage` argument, not any argument to `write()` itself
- `Line` must NOT be made generic (`Line[str]`) -- 254+ downstream subclasses set class-level `LINE = Line(fields)` without a type argument
- `# type: ignore` retained in `cfinterface/adapters/components/line/repository.py` on `field.read(line)` in `BinaryRepository.read()`

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

## TabularParser / TabularSection Pattern (Epic 06)

- `cfinterface/components/tabular.py` -- single file holding `ColumnDef`, `TabularParser`, and `TabularSection`; do NOT split into separate files
- `ColumnDef` is a `NamedTuple` with fields `name: str` and `field: Field` -- class-based form used (not functional); each `ColumnDef` must own its own `Field` instance because `Line.read()` mutates field values in place
- `TabularParser.__slots__ = ["_columns", "_delimiter", "_line"]` -- stores the columns list, the delimiter, and a single internal `Line` instance
- `TabularParser.__init__` signature: `(columns: List[ColumnDef], storage: Union[str, StorageType] = "", delimiter: Optional[Union[str, bytes]] = None)` -- storage default `""` matches `Line` convention; delimiter `None` selects fixed-width positional parsing
- `parse_lines()` catches broad `Exception` per row and fills the entire row with `None` -- do NOT let a single bad line abort the parse; row count always equals input line count
- `format_rows()` derives `n_rows` from `len(next(iter(data.values())))` -- guard handles empty dict; `Line.write()` appends `\n` so callers must account for it in round-trip tests
- `to_dataframe()` is a `@staticmethod` (not `@classmethod`) with lazy pandas import and `# type: ignore[name-defined]  # noqa: F821` on the return annotation because `pd.DataFrame` is not importable at module level
- `TabularSection.__slots__ = ["_parser", "_headers"]` -- do NOT add `"data"` to slots; `data` is a property defined on `Section` via name-mangled `__data`
- `TabularSection` class attributes: `COLUMNS: List[ColumnDef] = []`, `HEADER_LINES: int = 0`, `END_PATTERN: str = ""`, `DELIMITER: Optional[Union[str, bytes]] = None` -- all have safe defaults so the class is usable without subclassing
- `read()` seek-back pattern: `pos = file.tell()` before `readline()`; `file.seek(pos)` if `END_PATTERN` matches -- file pointer is rewound so the caller can still process the terminating line
- EOF detection uses `line == ""` (hard EOF); blank-line detection uses `len(line) <= 1` (matches inewave convention for `"\n"`)
- Header lines are stored verbatim including `\n` in `self._headers`; written back in `write()` before data lines
- `write()` guards `self.data is not None` before calling `format_rows()` -- avoids crash when section was never read
- `__eq__` uses `isinstance(o, self.__class__)` (exact class check, not `type(o) is type(self)`) and compares `self.data == o.data`

## Delimiter Support Convention (Epic 06)

- Delimiter support is entirely provided by the existing `Line` class (`cfinterface/components/line.py`) and `TextualRepository.__delimted_reading()` / `__delimted_writing()` -- do NOT reimplement
- For delimited `ColumnDef`, set `starting_position=0` by convention; the position is irrelevant but the field constructor requires it; use `size` large enough for the widest expected token
- `str.split(delimiter)` is used internally (no `csv` module) -- quoted fields are NOT supported; this matches all inewave file format conventions
- Multi-character delimiters work because `str.split()` handles them natively
- Delimiter threading: `TabularParser.__init__` -> `Line(fields, delimiter=delimiter, storage=storage)` -> `TextualRepository`; no additional code needed in `parse_lines()` or `format_rows()`

## Testing Patterns

- Test assertions on computed neighbors use `is` (identity), not `==` -- see `tests/data/test_registerdata.py`
- When replacing an algorithm, copy the original as a `_reference_*()` helper and fuzz-compare -- see `tests/components/test_floatfield.py`
- `pytest.importorskip("pandas")` pattern for tests that require optional pandas -- skips cleanly when pandas absent
- `patch.dict("sys.modules", {"pandas": None})` to simulate missing optional import in tests -- see `tests/components/test_tabular.py`
- Helper subclass fixtures defined at module level in test files (not inside test functions) -- see `_YearValueSection`, `_TwoHeaderSection`, `_EndPatternSection`, `_SemicolonSection` in `tests/components/test_tabular.py`
- `io.StringIO` for in-memory file mocking in Section read/write tests -- no temp files needed
- Test count: 331 after epic-06 (292 after epic-05 + 39 new)

## Key Files Reference

- `cfinterface/_utils/__init__.py` -- `_is_null(value: Any) -> bool`
- `cfinterface/storage.py` -- `StorageType(str, Enum)` and `_ensure_storage_type()`
- `cfinterface/components/field.py` -- module-level `_T`, `@overload` on `read()`/`write()`, simplified write body
- `cfinterface/components/line.py` -- `@overload` on `read()` only; `write()` stays `Union[str, bytes]`; delimiter parameter; `__delimted_reading()` / `__delimted_writing()`
- `cfinterface/components/register.py` -- `@overload` on `matches()`; `_container`/`_index`/fallback slots
- `cfinterface/components/block.py` -- `@overload` on `begins()`/`ends()`; same back-reference slots
- `cfinterface/components/tabular.py` -- `ColumnDef`, `TabularParser`, `TabularSection`; canonical reference for composition-based parser pattern
- `cfinterface/components/__init__.py` -- re-exports `ColumnDef`, `TabularParser`, `TabularSection`
- `cfinterface/adapters/components/repository.py` -- `_pattern_cache`, `_compile()`, three-overload `factory()`, narrowed concrete types
- `cfinterface/adapters/components/line/repository.py` -- three-overload `factory()`, narrowed concrete types, `# type: ignore` on binary field read
- `cfinterface/adapters/reading/repository.py` -- three-overload `factory()`, `BinaryIO`/`TextIO` filepointer types
- `cfinterface/adapters/writing/repository.py` -- three-overload `factory()`, `isinstance` guards retained for safety
- `cfinterface/components/floatfield.py` -- 3-attempt `_textual_write()` else-branch
- `cfinterface/data/registerdata.py`, `blockdata.py`, `sectiondata.py` -- `_items`, `_type_index`, `_refresh_indices`, `_index_of`, `_rebuild_type_index`
- `tests/components/test_tabular.py` -- 39 tests covering ColumnDef, TabularParser (fixed-width + delimited), TabularSection (read/write/round-trip/equality)

## Warnings for Future Epics

- Epic-07 schema versioning: `storage: Union[str, StorageType]` parameter threading is load-bearing and must not be narrowed in any method signature; `Literal["v1"]`/`Literal["v2"]` overloads on schema-version factory functions would work with the same three-overload pattern
- Epic-07 batch ops: `TabularSection` already produces a `Dict[str, List[Any]]` from `read()` -- batch operations can aggregate these dicts by appending lists; do NOT reinvent the parsing layer
- Epic-07: if a schema version affects column layout, the `COLUMNS` class attribute on a `TabularSection` subclass can be overridden per version via a class factory or `__init_subclass__` hook; do NOT modify `TabularParser` internals
- Any new data container must follow the `_items` + `_type_index` + `_refresh_indices` + `_index_of` + `_rebuild_type_index` pattern from `cfinterface/data/registerdata.py`
- Any new component class in a container must add `_container`, `_index`, `__previous_fallback`, `__next_fallback` to `__slots__` and implement the computed `previous`/`next`/`is_first`/`is_last` pattern from `cfinterface/components/register.py`
- Do NOT add truncation to `_textual_write()`; do NOT add module-level pandas imports
- Do NOT make `TabularParser` or any new parser class generic -- use `storage: Union[str, StorageType]` constructor argument instead
- `_compile()` / `_pattern_cache` from `cfinterface/adapters/components/repository.py` is available for reuse in any new pattern-matching logic
