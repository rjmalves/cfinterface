# ticket-027 Add Version Validation and Mismatch Detection

## Context

### Background

When NEWAVE updates its output format (e.g., from version 28 to 29.4), the sintetizador-newave pipeline silently produces incorrect data if the wrong version is specified. The `set_version()` mechanism (and the new `version` parameter from ticket-025) resolves to a component list, but there is no check that the resolved version's components actually match the file content. Registers that do not match any known pattern are silently captured as `DefaultRegister` / `DefaultBlock` / `DefaultSection`, and the consumer only discovers the mismatch downstream when data is missing or malformed.

This ticket adds a `validate_version()` method that compares the components found during a read against the components expected by the declared version, returning a structured result that consumers can inspect.

### Relation to Epic

This is the diagnostic/safety ticket of epic-07. It builds on ticket-024's `SchemaVersion` and `resolve_version()` and operates on the data structures produced by `read()`. It is not blocking any other ticket and provides independent value as a debugging aid for consumers.

### Current State

After `read()`, a file instance's `.data` property exposes a `RegisterData` / `BlockData` / `SectionData` container. Each container provides:

- `of_type(t)` -- iterator over items matching a type (with `issubclass` matching)
- Iteration over all items (including `DefaultRegister`/`DefaultBlock`/`DefaultSection` for unrecognized content)

The `DefaultRegister`, `DefaultBlock`, and `DefaultSection` classes serve as catch-all containers for lines/blocks/sections that did not match any declared component type. A high ratio of default-type items typically indicates a version mismatch.

The `VERSIONS` dict on each file class maps version strings to component type lists. After reading, we can compare: "the version says these types should be present" vs. "these types were actually found in the data."

## Specification

### Requirements

1. Create a `VersionMatchResult` named tuple in `cfinterface/versioning.py` with fields:
   - `matched: bool` -- `True` if all expected component types were found and fewer than `threshold` fraction of items are default-type
   - `expected_types: List[Type]` -- the component types from the resolved version
   - `found_types: List[Type]` -- the unique component types actually found in the data (excluding default types)
   - `missing_types: List[Type]` -- expected types that were not found in the data
   - `unexpected_types: List[Type]` -- types found in the data that are not in the expected list (excluding default types)
   - `default_ratio: float` -- fraction of items that are default-type (0.0 to 1.0)

2. Create a `validate_version()` function in `cfinterface/versioning.py`:

   ```python
   def validate_version(
       data: Union[RegisterData, BlockData, SectionData],
       expected_types: List[Type],
       default_type: Type,
       threshold: float = 0.5,
   ) -> VersionMatchResult:
   ```

   - Iterates over all items in `data`, categorizes them as expected, unexpected, or default
   - Computes `default_ratio` as `count(default_type items) / total items`
   - `matched` is `True` when `missing_types` is empty AND `default_ratio < threshold`

3. Add a `validate(self, version: Optional[str] = None, threshold: float = 0.5) -> VersionMatchResult` instance method to `RegisterFile`, `BlockFile`, and `SectionFile`:
   - If `version` is provided, resolves it against `cls.VERSIONS` to get expected types
   - If `version` is `None`, uses the current `cls.REGISTERS`/`cls.BLOCKS`/`cls.SECTIONS`
   - Calls `validate_version(self.data, expected_types, DefaultRegister/DefaultBlock/DefaultSection, threshold)`

4. Re-export `VersionMatchResult` and `validate_version` from `cfinterface/__init__.py`

### Inputs/Props

`validate_version()` function:

- `data` -- the file's data container (obtained from `file_instance.data`)
- `expected_types` -- the component type list for the declared version
- `default_type` -- the default/catch-all type for the file kind (`DefaultRegister`, `DefaultBlock`, or `DefaultSection`)
- `threshold` -- maximum acceptable fraction of default-type items (default `0.5` = 50%)

`file.validate()` instance method:

- `version` -- optional version string to validate against (default: use current class component list)
- `threshold` -- passed through to `validate_version()`

### Outputs/Behavior

- `validate()` returns a `VersionMatchResult` with all diagnostic fields populated
- `result.matched` is the primary boolean for quick checks
- The remaining fields provide detailed diagnostics for debugging
- No exceptions are raised -- the result is informational, and the consumer decides what to do

Example:

```python
f = MyRegisterFile.read("file.dat", version="28")
result = f.validate(version="28")
if not result.matched:
    print(f"Missing types: {result.missing_types}")
    print(f"Default ratio: {result.default_ratio:.1%}")
```

### Error Handling

- If `version` is provided to `validate()` but resolves to `None`, use the current class component list as fallback and set `matched = False` in the result (since we cannot validate against an unknown version)
- If the data container is empty (only the initial default item), `default_ratio` is `1.0` and `matched` is `False` (assuming threshold < 1.0)
- No exceptions -- this is a diagnostic tool, not a guard

## Acceptance Criteria

- [ ] Given a `RegisterFile` read with version `"v1"` components `[A, B]`, and the data contains instances of `A`, `B`, and `DefaultRegister`, when `validate(version="v1")` is called, then `result.matched` is `True`, `result.missing_types` is `[]`, and `result.default_ratio` is the fraction of DefaultRegister items
- [ ] Given the same file but the data only contains `DefaultRegister` instances (complete mismatch), when `validate(version="v1")` is called, then `result.matched` is `False`, `result.missing_types` is `[A, B]`, and `result.default_ratio` is `1.0`
- [ ] Given a file where one expected type `B` is missing from the data, when `validate(version="v1")` is called, then `result.matched` is `False` and `result.missing_types` is `[B]`
- [ ] Given `validate_version(data, expected_types, default_type, threshold=0.8)`, when 60% of items are default-type, then `result.matched` is `True` (if no missing types) because `0.6 < 0.8`
- [ ] Given `validate_version(data, expected_types, default_type, threshold=0.5)`, when 60% of items are default-type, then `result.matched` is `False` because `0.6 >= 0.5`
- [ ] Given `validate()` called without `version`, when `cls.REGISTERS` is `[A, B]`, then validation uses `[A, B]` as expected types
- [ ] Given `validate(version="v0")` where `"v0"` resolves to `None`, when called, then `result.matched` is `False`
- [ ] Given `from cfinterface import VersionMatchResult, validate_version`, when imported, then both are available
- [ ] Given the existing test suite, when `pytest` is run, then all existing tests still pass

## Implementation Guide

### Suggested Approach

1. In `cfinterface/versioning.py`, add `VersionMatchResult` as a class-based `NamedTuple`:

   ```python
   class VersionMatchResult(NamedTuple):
       matched: bool
       expected_types: List[Type]
       found_types: List[Type]
       missing_types: List[Type]
       unexpected_types: List[Type]
       default_ratio: float
   ```

2. Add `validate_version()` in the same module:
   - Count total items by iterating `data`
   - For each item, check `type(item)` -- use exact type, not `isinstance`, matching the `_type_index` pattern from epic-04 data containers
   - Build sets of found types, compute default count, derive missing/unexpected lists
   - Return `VersionMatchResult`

3. In each file class, add `validate()` instance method:

   ```python
   def validate(
       self,
       version: Optional[str] = None,
       threshold: float = 0.5,
   ) -> "VersionMatchResult":
       from cfinterface.versioning import validate_version, resolve_version
       if version is not None and self.__class__.VERSIONS:
           expected = resolve_version(version, self.__class__.VERSIONS)
           if expected is None:
               # Cannot validate against unknown version
               return validate_version(
                   self.data, self.__class__.REGISTERS, DefaultRegister, threshold
               )._replace(matched=False)
           return validate_version(self.data, expected, DefaultRegister, threshold)
       return validate_version(
           self.data, self.__class__.REGISTERS, DefaultRegister, threshold
       )
   ```

4. Update `cfinterface/__init__.py` to re-export `VersionMatchResult` and `validate_version`

### Key Files to Modify

- `cfinterface/versioning.py` -- add `VersionMatchResult` and `validate_version()`
- `cfinterface/files/registerfile.py` -- add `validate()` instance method
- `cfinterface/files/blockfile.py` -- add `validate()` instance method
- `cfinterface/files/sectionfile.py` -- add `validate()` instance method
- `cfinterface/__init__.py` -- add re-exports
- `tests/test_versioning.py` -- add `validate_version()` tests
- `tests/files/test_registerfile.py` -- add `validate()` tests
- `tests/files/test_blockfile.py` -- add `validate()` tests
- `tests/files/test_sectionfile.py` -- add `validate()` tests

### Patterns to Follow

- `NamedTuple` class-based form for `VersionMatchResult`, matching `SchemaVersion` and `ColumnDef` patterns
- `type(item)` for exact type matching, matching the `_type_index` pattern in `RegisterData`/`BlockData`/`SectionData`
- Lazy import of `validate_version` inside instance method body is NOT needed here -- `cfinterface.versioning` has no heavy dependencies
- Numpydoc docstrings for public API

### Pitfalls to Avoid

- Do NOT use `isinstance()` for type categorization -- `DefaultRegister` is a subclass of `Register`, so `isinstance(item, Register)` would match defaults; use `type(item) is DefaultRegister` for exact check
- Do NOT raise exceptions from `validate()` or `validate_version()` -- these are diagnostic functions
- Do NOT add automatic validation to `read()` -- validation is opt-in; automatic validation would break existing consumers that intentionally read with version-mismatched component lists
- The `data` parameter iterates over the container -- all three data containers support iteration (they have `__iter__` returning items). The first item is always the initial default instance from construction -- include it in the count
- `_replace()` on NamedTuple creates a copy with one field changed -- use this for the "unknown version" case rather than constructing a full result manually

## Testing Requirements

### Unit Tests

- Test `validate_version()` with all expected types found, low default ratio -> `matched=True`
- Test `validate_version()` with missing types -> `matched=False`
- Test `validate_version()` with high default ratio above threshold -> `matched=False`
- Test `validate_version()` with high default ratio below threshold -> `matched=True` (if no missing types)
- Test `validate_version()` with empty data (only default item) -> `default_ratio=1.0`, `matched=False`
- Test `VersionMatchResult` construction and field access
- Test `unexpected_types` detection (types found in data but not in expected list)
- Test threshold parameter at boundary values

### Integration Tests

- Test `file.validate(version="v1")` on a `VersionedRegisterFile` instance with matched content
- Test `file.validate(version="v1")` on a `VersionedRegisterFile` instance with mismatched content
- Test `file.validate()` without version parameter uses class default
- Test `file.validate(version="v0")` with unresolvable version

### E2E Tests (if applicable)

Not applicable.

## Dependencies

- **Blocked By**: ticket-024 (needs `resolve_version()` and `cfinterface/versioning.py` module)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
