# Epic 02 Learnings — Compile Regex and StorageType Enum

**Epic**: epic-02-compile-regex-and-storage-enum
**Tickets**: 005–009
**Date**: 2026-02-23
**Status**: Completed, all 223 tests pass

---

## Patterns Established

- **Module-level compiled-pattern cache**: A module-level `_pattern_cache: Dict[Union[str, bytes], re.Pattern]` dict combined with a `_compile(pattern)` helper is the correct caching strategy for patterns that originate from class-level constants. The lazy-on-first-use approach avoids issues with Register/Block/Section subclasses that may not be imported at module-load time. See `cfinterface/adapters/components/repository.py` lines 7–16.

- **`str, Enum` mixin for backward-compatible string enums**: `class StorageType(str, Enum)` with `TEXT = "TEXT"` and `BINARY = "BINARY"` is the canonical pattern for replacing string sentinels with type-safe members while preserving equality with the original strings. `hash(StorageType.TEXT) == hash("TEXT")` means dict lookups using string keys against `StorageType`-keyed dicts work transparently. See `cfinterface/storage.py`.

- **Single-point deprecation at the consumer entry point**: Deprecation warnings for string-typed storage values are emitted only inside the file-class `__init__` methods (`RegisterFile`, `BlockFile`, `SectionFile`) via `_ensure_storage_type()`, not inside hot per-line loops. This keeps the warning useful to consumers without impacting read-path performance. See `cfinterface/files/registerfile.py` line 30, `cfinterface/files/blockfile.py` line 30, `cfinterface/files/sectionfile.py` line 30.

- **Empty-string sentinel exempted from deprecation**: The internal `storage=""` default used in component method signatures is a non-consumer sentinel that triggers the TextualRepository fallback. `_ensure_storage_type` explicitly passes `""` through without warning. This distinction between internal defaults and consumer-set values is critical for a clean deprecation surface. See `cfinterface/storage.py` lines 29–30.

- **Union type hints at all storage boundaries**: All method parameters and class attributes that accept storage values use `Union[str, StorageType]` rather than just `StorageType`. This preserves backward compatibility for the 254+ downstream file subclasses that set `STORAGE = "TEXT"` as a plain string. See `cfinterface/components/register.py`, `cfinterface/components/block.py`, `cfinterface/components/defaultregister.py`.

---

## Architectural Decisions

- **`StorageType` module placed at package root (`cfinterface/storage.py`), not inside adapters**: Placing the enum in `cfinterface/storage.py` prevents circular imports. The adapter layer imports from components which import from storage; if storage lived inside adapters, it would create a cycle. The zero-dependency design of `storage.py` (only `enum` and `warnings` from stdlib) makes it importable everywhere safely.
  - Rejected: placing it inside `cfinterface/adapters/` — would create circular import risk
  - Rejected: placing it inside `cfinterface/components/` — components are above adapters in the dependency graph, so adapters importing from components is the existing direction; reversing would break layering

- **Factory dict keys use `StorageType` members, not strings**: Using `{StorageType.TEXT: TextualRepository, StorageType.BINARY: BinaryRepository}` rather than `{"TEXT": TextualRepository}` exploits the `str` mixin hash equality so both string and enum lookups work with a single dict. The alternative of keeping string keys and coercing the input would require explicit `StorageType(kind)` calls with error handling. See all four `factory()` functions.

- **`DefaultRegister` comparison changed from `storage not in ["BINARY"]` to `storage != StorageType.BINARY`**: The list-containment idiom `not in ["BINARY"]` does not work with `StorageType.BINARY` as input because list `__contains__` uses `==` which does work, but the idiom is misleading and fragile. The direct inequality comparison `!= StorageType.BINARY` is cleaner and works with both `"BINARY"` and `StorageType.BINARY` via the str mixin. See `cfinterface/components/defaultregister.py` lines 25 and 35.

---

## Files and Structures Created

- `cfinterface/storage.py` — New module containing `StorageType(str, Enum)` with `TEXT` and `BINARY` members, and the `_ensure_storage_type()` deprecation utility. This is the single source of truth for storage type representation.
- `tests/test_storage.py` — Unit tests for `StorageType` enum semantics (values, str comparison, construction from string, package-level import).
- `tests/test_storage_deprecation.py` — Unit tests for `_ensure_storage_type()` behavior (enum pass-through, string warns, empty-string exemption, file-subclass integration).
- `tests/adapters/components/test_pattern_cache.py` — Unit tests for `_compile()` cache identity, bytes pattern support, and distinct-pattern isolation.
- `tests/adapters/components/test_factory.py` — Integration tests verifying all four factory functions accept both string and enum inputs, and that the default fallback is preserved.
- `tests/components/test_storage_integration.py` — Tests verifying that `Register.matches()` and `Block.begins()` work correctly when called with `StorageType` members.

---

## Conventions Adopted

- `cfinterface/storage.py` docstrings use backtick-quoted code in the class docstring (e.g., ` `StorageType.TEXT == "TEXT"` `) consistent with existing numpydoc style; the `_ensure_storage_type()` function uses a shorter one-paragraph docstring without the `:param:` / `:rtype:` block because it is a private utility.
- All four `factory()` functions use the identical pattern: `mappings: Dict[Union[str, StorageType], Type[Repository]] = {StorageType.TEXT: ..., StorageType.BINARY: ...}; return mappings.get(kind, TextualRepository)`. Maintaining identical structure across all four adapter layers makes the pattern easy to locate and follow.
- `_ensure_storage_type` and `StorageType` are both exported from `cfinterface/storage.py` but only `StorageType` is re-exported from `cfinterface/__init__.py`. `_ensure_storage_type` is private API, accessed via direct module import in file classes.
- Test files for private internals (`_compile`, `_pattern_cache`, `_ensure_storage_type`) use `_pattern_cache.clear()` for isolation between test cases rather than module reloading, following the existing test style.

---

## Surprises and Deviations

- **No deviation**: The implementation matched the ticket specifications closely. The dict-key approach for factory functions (using `StorageType` members as keys, relying on hash equality with strings) worked exactly as specified in ticket-007, with no need for explicit string-to-enum coercion at lookup time.

- **`_ensure_storage_type` docstring was shortened**: The ticket specified a full `:param:` / `:rtype:` numpydoc block for `_ensure_storage_type`, but the implementation uses a one-paragraph summary only. This aligns with the convention established in epic-01 for private helpers. No behavioral difference; just a style consolidation. See `cfinterface/storage.py` lines 19–26.

- **`test_storage_deprecation.py` received two extra tests beyond the ticket spec**: The ticket specified four unit tests; the implementation added `test_file_subclass_with_string_storage_warns` and `test_file_subclass_with_enum_storage_no_warning` as integration-level deprecation tests covering the `RegisterFile.__init__` path. These are higher-value tests than isolated unit tests for the same behavior. See `tests/test_storage_deprecation.py` lines 40–64.

- **Test count grew from 200 to 223**: Epic-02 added 23 new tests across 5 new test files, all green.

---

## Recommendations for Future Epics

- Epic-03 rewrites `FloatField._textual_write()`. The storage layer is now stable; `FloatField` does not use the `storage` parameter directly, so no interaction is expected. However, if any FloatField path reads `self.value` and passes it through a repository, ensure the `StorageType` comparisons in `DefaultRegister` remain unchanged.

- Epic-05 (type-safe text/binary dispatch) will likely add overloads or generic types to the four `factory()` functions. The current `Union[str, StorageType]` signature in all four files (`cfinterface/adapters/components/repository.py`, `cfinterface/adapters/components/line/repository.py`, `cfinterface/adapters/reading/repository.py`, `cfinterface/adapters/writing/repository.py`) is the correct starting point.

- Any new file class (e.g., a future `TabularFile`) that inherits the `STORAGE` class attribute pattern MUST call `_ensure_storage_type(self.__class__.STORAGE)` in its `__init__`, not pass `STORAGE` directly to the reading/writing layer. The deprecation guard lives at instantiation time, not inside reading loops.

- The `_pattern_cache` in `cfinterface/adapters/components/repository.py` is a module-level mutable dict. It is safe under the GIL for single-process use. If multi-threaded readers are ever introduced, document that `_compile()` has a benign double-write race (two threads may compile the same pattern, but will store an equivalent result) and does not require locking.
