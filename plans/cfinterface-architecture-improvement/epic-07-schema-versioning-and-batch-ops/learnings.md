# Epic-07 Learnings — Schema Versioning and Batch Operations

**Tickets covered**: ticket-024, ticket-025, ticket-026, ticket-027
**Test count after epic**: 391 (was 331 after epic-06, +60 new tests)

---

## Patterns Established

- **Single-module versioning**: `cfinterface/versioning.py` is a single flat module holding all four versioning exports (`SchemaVersion`, `resolve_version`, `VersionMatchResult`, `validate_version`). The function count (two) and NamedTuple count (two) comfortably fit in one file; no subpackage was created. This follows the same decision as `cfinterface/storage.py` for `StorageType`.
- **Keyword-only `version` parameter after `*args`**: The `read()` classmethod on all three file classes gained `version: Optional[str] = None` placed after `*args` to keep it keyword-only without changing any positional argument order. This is the correct Python pattern when a method already accepts `*args` and a new optional feature parameter must not break existing call sites.
- **Deprecation via `warnings.warn` with `stacklevel=2`**: `set_version()` was deprecated using `warnings.warn(..., DeprecationWarning, stacklevel=2)`, matching the exact stacklevel convention established in `cfinterface/storage.py`. The deprecation message points callers to `read(content, version="...")` by name.
- **`resolve_version()` replaces inline copy-paste**: The three-line version resolution logic (sort keys, filter `requested >= key`, take last) was copy-pasted identically in `RegisterFile`, `BlockFile`, and `SectionFile`. It is now centralised in `cfinterface/versioning.py` and both `read()` (inline) and `set_version()` delegate to it.
- **`TYPE_CHECKING` guard for circular import avoidance**: Each file class imports `VersionMatchResult` under `if TYPE_CHECKING:` to avoid loading `cfinterface.versioning` at module import time unnecessarily. The `validate()` method uses a local import inside its body as a secondary guard. This pattern was not strictly required (versioning has no circular deps) but was used defensively.
- **`NamedTuple._replace()` for partial override**: In `validate()` when a version resolves to `None`, the implementation calls `validate_version(...).` `_replace(matched=False)` to produce a fully-populated result with the forced failure flag. This avoids constructing a six-field NamedTuple manually and reduces the chance of field-order bugs.
- **`type(item) is default_type` for exact categorisation**: `validate_version()` uses `type(item) is default_type` (identity comparison on the type object) rather than `isinstance`. This is critical because `DefaultRegister`, `DefaultBlock`, and `DefaultSection` are concrete subclasses of `Register`, `Block`, and `Section` respectively. `isinstance` would misclassify real components as defaults.

---

## Architectural Decisions

- **`SchemaVersion` as a `NamedTuple`, not a `dataclass`**: Rejected `dataclass` because `NamedTuple` is immutable and hashable by default, matching the `ColumnDef` precedent from epic-06. `SchemaVersion` is not a container for mutable state; it is a descriptor. Immutability is a feature.
- **`VersionMatchResult` as a `NamedTuple` with no defaults**: All six fields are required at construction time. This was intentional to prevent partially-initialised results from existing. The `_replace()` pattern is used when a single field override is needed rather than adding optional defaults that could produce ambiguous states.
- **`read_many()` as a one-liner dict comprehension, no parallelism**: The ticket explicitly rejected `concurrent.futures` and error-collection approaches. The implementation is `{path: cls.read(path, version=version) for path in paths}`, which is trivially auditable and delegates all logic to `read()`. Fail-fast behaviour is inherited automatically from the comprehension evaluation order.
- **Lexicographic string comparison preserved**: `resolve_version()` preserves the existing `sorted(keys)` + `requested >= ver` lexicographic comparison from the old `set_version()`. This was explicitly NOT changed to semantic versioning because 254+ downstream subclasses (inewave package) define VERSIONS keys as arbitrary strings like `"28"`, `"28.16"`, `"29.4.1"`. Any change to the comparison semantic would be a breaking change without a migration path.
- **`validate()` is opt-in, not automatic**: Automatic validation was considered and rejected. Adding validation inside `read()` would break consumers that intentionally read with version-mismatched component lists (e.g., during format migrations). The diagnostic tool is only invoked when the consumer calls `file.validate()` explicitly.
- **`default_ratio = 1.0` for empty data**: When the data container is empty (total items = 0), `validate_version()` returns `default_ratio = 1.0` and `matched = False`. This was chosen as a safe conservative fallback: an empty file cannot be validated as a correct match.

---

## Files and Structures Created

- `cfinterface/versioning.py` — New module. Contains `SchemaVersion` (NamedTuple: `key`, `components`, `description`), `resolve_version()` (extracts the copy-paste version resolution logic), `VersionMatchResult` (NamedTuple: `matched`, `expected_types`, `found_types`, `missing_types`, `unexpected_types`, `default_ratio`), and `validate_version()`. Zero intra-package dependencies except `typing`.
- `tests/test_versioning.py` — New test file at the `tests/` root level (not in a subdirectory), corresponding to the new top-level `cfinterface/versioning.py` module. Contains 18 tests: 10 for `SchemaVersion`/`resolve_version` (ticket-024) and 8 for `VersionMatchResult`/`validate_version` (ticket-027).

---

## Conventions Adopted

- **`TYPE_CHECKING` guard for return-type annotations on file methods**: When a method returns a type defined in a module that could theoretically create an import cycle, use `if TYPE_CHECKING: from cfinterface.versioning import VersionMatchResult` and annotate the return type as a string `"VersionMatchResult"`. This was adopted uniformly across all three file classes in `cfinterface/files/`.
- **Test file placement for new top-level modules**: A new top-level module (`cfinterface/versioning.py`) gets its own test file at `tests/test_versioning.py`, not inside a subdirectory. Subdirectory test files (`tests/files/`, `tests/components/`) are for modules that mirror existing subdirectory structure. New top-level modules get top-level test files.
- **Mid-file imports in test files**: Tests for `VersionMatchResult` and `validate_version` are appended to `tests/test_versioning.py` with a bare import at the mid-file boundary (`from cfinterface.versioning import VersionMatchResult, validate_version  # noqa: E402`). The same pattern appears in `tests/files/test_registerfile.py`, `test_blockfile.py`, and `test_sectionfile.py`. This avoids splitting into separate files for tightly related functionality added in the same epic.
- **`found_types` / `missing_types` / `unexpected_types` sorted by `__name__`**: The `validate_version()` function sorts these lists by `t.__name__` before storing them in `VersionMatchResult`. This ensures deterministic output regardless of set iteration order, which makes test assertions on list membership predictable.

---

## Surprises and Deviations

- **No deviation from planned approach**: All four tickets were implemented exactly as specified. The `NamedTuple` with defaults, keyword-only parameter, `stacklevel=2`, and `_replace()` techniques were all used as documented. No workarounds were required.
- **`validate_version()` receives a plain iterable, not a typed container**: The function signature uses untyped `data` (no type annotation). This was intentional: all three data containers (`RegisterData`, `BlockData`, `SectionData`) support `__iter__` but share no common base class. A `Union[RegisterData, BlockData, SectionData]` annotation would have worked but added no runtime value. The test suite also passes plain lists to `validate_version()` directly, confirming the duck-typing approach is correct and sufficient.
- **`data` parameter in `validate_version()` is `Any`-typed**: The ticket suggested `Union[RegisterData, BlockData, SectionData]` as the type annotation. The implementation left it unannotated (`data`). This avoids importing all three data container types into `cfinterface/versioning.py`, which would introduce intra-package dependencies that the module was designed to avoid. The tradeoff is slightly weaker static typing in exchange for cleaner dependency topology.
- **60 new tests, not the ~30 estimated**: The test count grew from 331 to 391, a gain of 60. The ticket estimates implied roughly 10-15 tests per ticket but each ticket had tests on all three file classes (register, block, section) and the versioning module itself, tripling the expected count.

---

## Recommendations for Future Developers

- When adding new per-read parameters to `RegisterFile.read()`, `BlockFile.read()`, or `SectionFile.read()`, always place them after `*args` as keyword-only parameters. Positional parameters after `cls` and `content` break sintetizador-newave which calls `read(path)` positionally. See `cfinterface/files/registerfile.py` line 67 for the `version: Optional[str] = None` placement.
- `resolve_version()` in `cfinterface/versioning.py` is the single source of truth for version key resolution. Do not reimplement the sort-and-filter logic in any new code. Both `read()` and `set_version()` delegate to it.
- If a future epic adds per-instance caching of the resolved version (e.g., to avoid repeated `resolve_version()` calls when `validate()` is called multiple times), the `__slots__` on all three file classes must be extended. Currently `__slots__ = ["__data", "__storage", "__encoding"]` and there is no slot for version state.
- The `validate_version()` function works on any iterable of objects. It can be reused with any container type that yields typed items. Do not add container-specific logic into it.
- When writing tests for `validate()` on file classes, note that the data container always contains an initial default instance from construction (e.g., `DefaultRegister(data="")`). Tests must account for this initial default item in `default_ratio` calculations. See `tests/files/test_registerfile.py` line 236.
