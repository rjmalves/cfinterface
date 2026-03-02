# ticket-025 Implement Instance-Level Version Binding for File Classes

## Context

### Background

The current `set_version()` classmethod on `RegisterFile`, `BlockFile`, and `SectionFile` mutates the class-level `REGISTERS`/`BLOCKS`/`SECTIONS` attribute. This is not thread-safe and causes a subtle coupling problem: calling `Cmargmed.set_version("28")` in one part of the codebase affects every subsequent `Cmargmed.read()` call everywhere, including in other threads or coroutines.

The consumer pattern in sintetizador-newave is:

```python
reader.set_version(self.__version)   # mutates class state
return reader.read(path).valores     # reads with mutated state
```

This ticket adds a `version` parameter to the `read()` classmethod so that version binding happens per-call rather than per-class. The existing `set_version()` classmethod is preserved with a deprecation warning for backward compatibility.

### Relation to Epic

This is the core ticket of epic-07. It replaces the fragile class-mutation pattern with a clean per-read version parameter. Ticket-024 provides the `resolve_version()` utility that this ticket uses internally. Ticket-026 (batch read) builds on the `version` parameter introduced here.

### Current State

All three file classes share this identical structure (using `RegisterFile` as example):

```python
class RegisterFile:
    __slots__ = ["__data", "__storage", "__encoding"]
    VERSIONS: Dict[str, List[Type[Register]]] = {}
    REGISTERS: List[Type[Register]] = []
    __VERSION = "latest"

    @classmethod
    def read(cls, content: Union[str, bytes], *args, **kwargs):
        reader = RegisterReading(cls.REGISTERS, cls.STORAGE, *args, **kwargs)
        # ... encoding loop ...

    @classmethod
    def set_version(cls, v: str):
        available_versions = sorted(cls.VERSIONS.keys())
        recent_versions = [ver for ver in available_versions if v >= ver]
        if recent_versions:
            cls.__VERSION = v
            cls.REGISTERS = cls.VERSIONS.get(recent_versions[-1], cls.REGISTERS)
```

The `read()` classmethod uses `cls.REGISTERS` (class-level), which is only correct if `set_version()` was called before `read()`. The `__VERSION` private attribute is set but never used beyond storage.

## Specification

### Requirements

1. Add an optional `version: Optional[str] = None` keyword parameter to `read()` on all three file classes
2. When `version` is provided, use `resolve_version(version, cls.VERSIONS)` to determine the component list for that specific read call -- do NOT mutate `cls.REGISTERS`/`cls.BLOCKS`/`cls.SECTIONS`
3. When `version` is `None` (default), use `cls.REGISTERS`/`cls.BLOCKS`/`cls.SECTIONS` as before -- this preserves full backward compatibility including with the old `set_version()` pattern
4. Add a `warnings.warn()` deprecation warning to `set_version()` on all three file classes, advising to use `read(content, version="...")` instead
5. Replace the inline version resolution logic in `set_version()` with a call to `resolve_version()` from `cfinterface.versioning`
6. All changes must preserve backward compatibility -- existing consumer code using `set_version()` + `read()` must continue to work identically, just with a `DeprecationWarning`

### Inputs/Props

Modified `read()` signature for `RegisterFile`:

```python
@classmethod
def read(cls, content: Union[str, bytes], *args, version: Optional[str] = None, **kwargs):
```

Same pattern for `BlockFile.read()` and `SectionFile.read()`.

The `version` parameter is keyword-only (after `*args`) to avoid breaking existing positional argument usage.

### Outputs/Behavior

- `MyFile.read("file.dat")` -- uses `cls.REGISTERS` as before (no change)
- `MyFile.read("file.dat", version="28.16")` -- resolves version internally, uses resolved component list for this call only, does NOT mutate `cls.REGISTERS`
- `MyFile.read("file.dat", version="28.16")` followed by `MyFile.read("file.dat")` -- second call uses `cls.REGISTERS` (class default), not `"28.16"`
- `MyFile.set_version("28.16")` -- works as before but emits `DeprecationWarning`

### Error Handling

- If `version` is provided but `resolve_version()` returns `None` (no matching version), fall back to `cls.REGISTERS`/`cls.BLOCKS`/`cls.SECTIONS` and emit a `warnings.warn()` with a message like `"No matching version for '{version}' in {cls.__name__}.VERSIONS. Using default components."`
- If `cls.VERSIONS` is empty and `version` is provided, same fallback behavior

## Acceptance Criteria

- [ ] Given `VersionedRegisterFile` with `VERSIONS = {"v1": [A], "v2": [B]}` and `REGISTERS = [B]`, when `VersionedRegisterFile.read(content, version="v1")` is called, then the file is parsed using component list `[A]`, and `VersionedRegisterFile.REGISTERS` is still `[B]` afterward
- [ ] Given the same setup, when `VersionedRegisterFile.read(content)` is called (no version), then the file is parsed using `cls.REGISTERS` (which is `[B]`)
- [ ] Given `VersionedRegisterFile.set_version("v1")` is called, when warnings are captured, then a `DeprecationWarning` is emitted with message containing `"read(content, version="` as the recommended alternative
- [ ] Given `VersionedRegisterFile.set_version("v1")` is called, when `VersionedRegisterFile.REGISTERS` is inspected, then it equals `[A]` (backward-compatible mutation still works)
- [ ] Given `VersionedBlockFile` and `VersionedSectionFile`, when the same patterns are tested, then identical behavior is observed
- [ ] Given a version that resolves to `None` (e.g., `"v0"` when VERSIONS has `"v1"` and `"v2"`), when `read(content, version="v0")` is called, then it falls back to `cls.REGISTERS` and emits a warning
- [ ] Given the existing 331+ tests, when `pytest` is run, then all pass (the three `test_*file_set_version` tests will now emit `DeprecationWarning` but still pass)

## Implementation Guide

### Suggested Approach

1. In `cfinterface/files/registerfile.py`:
   - Add `from cfinterface.versioning import resolve_version` import
   - Add `import warnings` import
   - Modify `read()` to accept `version: Optional[str] = None` as keyword-only parameter
   - Inside `read()`, compute `components = cls.REGISTERS` as default; if `version is not None and cls.VERSIONS`, call `resolved = resolve_version(version, cls.VERSIONS)` and use `resolved if resolved is not None else cls.REGISTERS`; if `resolved is None`, emit a warning
   - Pass `components` (instead of `cls.REGISTERS`) to `RegisterReading(...)`
   - In `set_version()`, add `warnings.warn("set_version() is deprecated. Use read(content, version='...') instead.", DeprecationWarning, stacklevel=2)` at the top
   - Replace the inline resolution logic in `set_version()` with `resolved = resolve_version(v, cls.VERSIONS); if resolved is not None: cls.REGISTERS = resolved`
2. Repeat the identical pattern for `blockfile.py` (using `cls.BLOCKS`, `BlockReading`) and `sectionfile.py` (using `cls.SECTIONS`, `SectionReading`)
3. Add tests in the existing test files: `tests/files/test_registerfile.py`, `tests/files/test_blockfile.py`, `tests/files/test_sectionfile.py`

### Key Files to Modify

- `cfinterface/files/registerfile.py` -- add `version` param to `read()`, deprecate `set_version()`
- `cfinterface/files/blockfile.py` -- same changes
- `cfinterface/files/sectionfile.py` -- same changes
- `tests/files/test_registerfile.py` -- add tests for `version` parameter and deprecation warning
- `tests/files/test_blockfile.py` -- same
- `tests/files/test_sectionfile.py` -- same

### Patterns to Follow

- `warnings.warn(..., DeprecationWarning, stacklevel=2)` pattern from `cfinterface/storage.py` (`_ensure_storage_type`) -- same stacklevel convention
- Keyword-only parameter after `*args` to avoid breaking existing positional usage
- The `version` parameter is `Optional[str]` with `None` default -- do NOT use empty string as sentinel (empty string `""` has special meaning in the storage system)

### Pitfalls to Avoid

- Do NOT change the `read()` return type or the `cls(...)` construction pattern
- Do NOT remove or rename `set_version()` -- it must remain functional for backward compatibility, just deprecated
- Do NOT make `version` a positional parameter -- existing consumers pass `content` positionally and may pass additional `*args` (e.g., `linesize` in `RegisterReading`)
- The `__VERSION` class attribute is unused downstream and can remain as-is in `set_version()` -- do NOT add it to `read()` or instance state
- Be careful with `__slots__` -- no new instance attributes are needed because the version is resolved within `read()` and discarded

## Testing Requirements

### Unit Tests

- Test `read(content, version="v1")` resolves correctly without mutating class state
- Test `read(content, version="v3")` (above all versions) resolves to highest available
- Test `read(content, version="v0")` (below all versions) falls back to default with warning
- Test `read(content)` (no version) continues to use class-level component list
- Test `set_version()` emits `DeprecationWarning` (use `pytest.warns(DeprecationWarning)`)
- Test `set_version()` still mutates class state (backward compat)
- All the above for `RegisterFile`, `BlockFile`, and `SectionFile`

### Integration Tests

- Test the common consumer pattern: `set_version("v1")` then `read()` still works (with deprecation warning)
- Test mixing: `set_version("v1")`, then `read(content, version="v2")` uses v2, then `read(content)` uses v1 (from the class mutation)

### E2E Tests (if applicable)

Not applicable.

## Dependencies

- **Blocked By**: ticket-024 (needs `resolve_version()`)
- **Blocks**: ticket-026

## Effort Estimate

**Points**: 3
**Confidence**: High
