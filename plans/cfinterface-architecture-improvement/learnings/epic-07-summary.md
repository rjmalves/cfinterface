# Accumulated Learnings — Epics 01–07

**As of**: 2026-02-23
**Covers**: epic-01 (tickets 001–004), epic-02 (tickets 005–009), epic-03 (tickets 010–011),
epic-04 (tickets 012–016), epic-05 (tickets 017–020), epic-06 (tickets 021–023),
epic-07 (tickets 024–027)

---

## Codebase Conventions

- `cfinterface/_utils/__init__.py` — designated home for private, dependency-free internal helpers
- `cfinterface/storage.py` — home for `StorageType` and `_ensure_storage_type()`; imports only `enum` and `warnings`; zero intra-package dependencies
- `cfinterface/versioning.py` — home for `SchemaVersion`, `resolve_version`, `VersionMatchResult`, `validate_version`; zero intra-package dependencies; do NOT add imports of data-container or file-class types
- Private utilities use one-line docstrings; full numpydoc is reserved for public API classes
- All Field write methods use `self.value is not None and not _is_null(self.value)` — explicit `is not None` is a fast path, do not collapse it
- Optional dependency methods use `try: import X except ImportError: raise ImportError("... pip install cfinterface[X]")` inside the method body
- New tests are appended to existing test files, not placed in separate files (confirmed across all epics)
- New top-level modules (e.g., `cfinterface/versioning.py`) get their own top-level test file at `tests/test_<module>.py`
- `tests/_utils/` — location for tests of `cfinterface/_utils/` helpers; `tests/files/` mirrors `cfinterface/files/`

## Dependency and Environment

- Test/dev installs must use `pip install -e ".[dev]"` — bare install no longer includes pandas; only `numpy` is a hard runtime dependency
- Do not add new dev dependencies without explicit approval; use stdlib alternatives
- Do NOT create a new `_utils/` submodule unless helper count exceeds three or four functions

## Storage Type Pattern

- `StorageType(str, Enum)` with `TEXT = "TEXT"` and `BINARY = "BINARY"` in `cfinterface/storage.py` — do NOT use `enum.StrEnum` (Python 3.11+ only)
- All four `factory()` functions use `StorageType` members as dict keys; all method parameters use `Union[str, StorageType]` — never narrow, because 254+ downstream subclasses set `STORAGE = "TEXT"` as a plain string
- The internal `storage=""` default is a sentinel for the TextualRepository fallback — it is NOT deprecated
- Any new file class using the `STORAGE` attribute pattern MUST call `_ensure_storage_type(self.__class__.STORAGE)` in `__init__`

## Typing and Overload Conventions (Epic 05)

- Module-level `_T = TypeVar("_T", str, bytes)` in `cfinterface/components/field.py` — TypeVars used in `@overload` stacks MUST be module-level; class-level TypeVars break the overload mechanism
- `@overload` stub bodies use `...` only — no docstring, no logic; docstrings live on the implementation method
- Three-overload `factory()` pattern: `Literal["TEXT"] -> TextualRepository`, `Literal["BINARY"] -> BinaryRepository`, `Union[str, StorageType] -> Repository` (fallback) — the fallback overload is required for runtime-value call sites
- Abstract `Repository` base class retains `Union[str, bytes]` in all signatures; only concrete subclasses narrow
- `Line.write()` return type is permanently `Union[str, bytes]` — cannot be overloaded because the discriminator is the constructor `storage` argument, not any argument to `write()`
- `Line` must NOT be made generic — 254+ downstream subclasses set class-level `LINE = Line(fields)` without a type argument

## Version Parameter and Deprecation Conventions (Epic 07)

- New keyword-only parameters on `read()` go after `*args` as `param: Optional[T] = None` — positional args before `*args` cannot change without breaking sintetizador-newave call sites
- `warnings.warn(..., DeprecationWarning, stacklevel=2)` — use `stacklevel=2` consistently; this is the established convention from `storage.py` and now `set_version()`
- `resolve_version()` in `cfinterface/versioning.py` is the single source of truth for version key resolution — do NOT reimplement the sort-filter logic anywhere
- Lexicographic string comparison (`sorted(keys)` + `requested >= ver`) must NOT be changed — 254+ downstream subclasses use arbitrary string version keys
- `TYPE_CHECKING` guard for return-type annotations when the return type lives in a module that could create import cycles: `if TYPE_CHECKING: from cfinterface.versioning import VersionMatchResult`
- `NamedTuple._replace()` is the correct way to produce a copy of a result with one field overridden — avoids manual six-field construction and field-order bugs

## NamedTuple Pattern

- All public descriptor/result types use class-based `NamedTuple` form: `ColumnDef` (epic-06), `SchemaVersion`, `VersionMatchResult` (epic-07)
- Prefer `NamedTuple` over `dataclass` for immutable descriptors and result types — immutability and hashability by default
- `VersionMatchResult` has no default values (all six fields required) — forces callers to construct fully-populated results
- `SchemaVersion` has `description: str = ""` as a default — purely optional metadata field

## Regex Pattern Cache

- Module-level `_pattern_cache: Dict[Union[str, bytes], re.Pattern]` + `_compile(pattern)` in `cfinterface/adapters/components/repository.py` — reusable for any new pattern-matching logic

## FloatField Write Optimization

- `_textual_write()` uses at most 3 `str.format()` calls: full precision, precision minus excess, precision minus one more for rounding-carry; overflow is intentionally preserved

## Data Container Pattern (Epic 04)

- All three containers use `__slots__ = ["_items", "_type_index"]` — `cfinterface/data/registerdata.py` is canonical
- `_index_of(self, item) -> int` uses identity scan (`r is item`) — `Block.__eq__` and `Section.__eq__` raise `NotImplementedError`
- `_type_index` maps exact `type(item)` keys; `of_type(t)` matches with `issubclass(key, t)`
- Data containers always contain at least one initial default instance from construction — account for this in `default_ratio` calculations in `validate_version()`

## Component Back-Reference Pattern (Epic 04)

- Each `Register`, `Block`, `Section` has `_container` and `_index` in `__slots__` — single-underscore prevents name mangling
- `previous`/`next`/`is_first`/`is_last` check `_container is not None` first; fall back to `__previous_fallback`/`__next_fallback` for orphaned components

## TabularParser / TabularSection Pattern (Epic 06)

- `cfinterface/components/tabular.py` — single file holding `ColumnDef`, `TabularParser`, `TabularSection`
- `ColumnDef` is a `NamedTuple`; each `ColumnDef` must own its own `Field` instance because `Line.read()` mutates in place
- `parse_lines()` catches broad `Exception` per row and fills the row with `None` — never aborts on a single bad line
- `read()` seek-back pattern: `pos = file.tell()` before `readline()`; `file.seek(pos)` if `END_PATTERN` matches
- EOF detection: `line == ""` (hard EOF); blank-line detection: `len(line) <= 1`

## Validation Pattern (Epic 07)

- `validate_version(data, expected_types, default_type, threshold)` in `cfinterface/versioning.py` accepts any iterable — duck-typing, no common base class required
- Use `type(item) is default_type` (exact identity), NOT `isinstance` — `DefaultRegister` is a subclass of `Register`, so `isinstance` would misclassify defaults as real components
- `validate()` on file classes is opt-in only — do NOT add automatic validation to `read()`; consumers may intentionally read with version-mismatched component lists
- `default_ratio = 1.0` when total items is zero — safe conservative fallback for empty data

## Batch API Pattern (Epic 07)

- `read_many(cls, paths: List[str], *, version: Optional[str] = None)` is a one-liner dict comprehension delegating entirely to `read()`
- Do NOT add `concurrent.futures`, error collection, or encoding overrides to `read_many()` — fail-fast is the correct default; consumers add parallelism if needed
- `read_many([])` returns `{}` — empty input, empty output, no special casing needed

## Testing Patterns

- `pytest.warns(DeprecationWarning, match="set_version.*deprecated")` — use `match=` parameter to verify message content
- `warnings.catch_warnings(record=True)` + `warnings.simplefilter("always")` for capturing warning count and message text in non-pytest-warns contexts
- `warnings.catch_warnings()` + `warnings.simplefilter("ignore", DeprecationWarning)` to suppress deprecation warnings in tests that verify the mutation side-effect of `set_version()` only
- `pytest.importorskip("pandas")` for tests requiring optional pandas
- `patch.dict("sys.modules", {"pandas": None})` to simulate missing optional import
- Test assertions on computed neighbors use `is` (identity), not `==`
- Mid-file imports (`# noqa: E402`) are acceptable in test files when a second logical group of tests needs types imported after the first group is defined

## Key Files Reference

- `cfinterface/_utils/__init__.py` — `_is_null(value: Any) -> bool`
- `cfinterface/storage.py` — `StorageType(str, Enum)` and `_ensure_storage_type()`
- `cfinterface/versioning.py` — `SchemaVersion`, `resolve_version`, `VersionMatchResult`, `validate_version`; canonical reference for lexicographic version resolution
- `cfinterface/components/field.py` — module-level `_T`, `@overload` on `read()`/`write()`
- `cfinterface/components/line.py` — `@overload` on `read()` only; delimiter parameter
- `cfinterface/components/tabular.py` — `ColumnDef`, `TabularParser`, `TabularSection`
- `cfinterface/files/registerfile.py` — `read(version=)`, `read_many()`, `validate()`, deprecated `set_version()`
- `cfinterface/files/blockfile.py` — same pattern as registerfile
- `cfinterface/files/sectionfile.py` — same pattern as registerfile
- `cfinterface/adapters/components/repository.py` — `_pattern_cache`, `_compile()`, three-overload `factory()`
- `cfinterface/data/registerdata.py` — canonical data container: `_items`, `_type_index`, `_refresh_indices`
- `tests/test_versioning.py` — 18 tests for `SchemaVersion`, `resolve_version`, `VersionMatchResult`, `validate_version`
- `tests/files/test_registerfile.py` — includes version parameter, `read_many`, `validate` tests (appended)
