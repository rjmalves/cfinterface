# ticket-024 Design SchemaVersion Descriptor and Version Resolution Utility

## Context

### Background

The current versioning system across `RegisterFile`, `BlockFile`, and `SectionFile` uses a `VERSIONS: Dict[str, List[Type[Component]]]` class attribute and a `set_version(cls, v: str)` classmethod. The version resolution logic -- sort keys, filter by `v >= ver`, take `recent_versions[-1]` -- is copy-pasted identically across all three file classes. This ticket extracts the version resolution into a standalone utility function and introduces a lightweight `SchemaVersion` descriptor that documents what a version entry contains.

The existing consumer packages (inewave, sintetizador-newave) use arbitrary string keys for version identifiers: `"27"`, `"28"`, `"28.12"`, `"28.16"`, `"29.2"`, `"29.4.1"`, `"latest"`. These are compared lexicographically via Python's `>=` operator on strings. This ticket preserves that exact comparison semantic -- it does NOT introduce semantic versioning or any new ordering scheme.

### Relation to Epic

This is the foundation ticket for epic-07. It creates the shared version resolution logic that ticket-025 (instance-level binding) will use, and the `SchemaVersion` descriptor that ticket-027 (validation) will inspect. By extracting the duplicated logic into a single function, the subsequent tickets can modify version behavior in one place.

### Current State

Each of the three file classes contains an identical `set_version()` implementation:

```python
# In RegisterFile, BlockFile, SectionFile (identical pattern):
@classmethod
def set_version(cls, v: str):
    available_versions = sorted(cls.VERSIONS.keys())
    recent_versions = [ver for ver in available_versions if v >= ver]
    if recent_versions:
        cls.__VERSION = v
        cls.REGISTERS = cls.VERSIONS.get(recent_versions[-1], cls.REGISTERS)
```

There is no `cfinterface/versioning/` module. The version resolution logic has no unit tests of its own -- it is only tested indirectly through `test_registerfile_set_version`, `test_blockfile_set_version`, and `test_sectionfile_set_version` in `tests/files/`.

## Specification

### Requirements

1. Create a `SchemaVersion` named tuple with fields: `key: str` (the version string, e.g. `"28.16"`), `components: List[Type]` (the register/block/section types for this version), and `description: str` (optional human-readable note, default `""`)
2. Create a `resolve_version(requested: str, versions: Dict[str, List[Type]]) -> Optional[List[Type]]` function that encapsulates the existing resolution logic: sort keys, filter `requested >= key`, return the component list for the last matching key, or `None` if no match
3. Both `SchemaVersion` and `resolve_version` live in a new module `cfinterface/versioning.py` (single file, NOT a subpackage -- following the convention from learnings that new `_utils/` submodules are avoided unless function count is high)
4. Re-export `SchemaVersion` and `resolve_version` from `cfinterface/__init__.py`
5. Do NOT modify any file class in this ticket -- ticket-025 will integrate the utility

### Inputs/Props

- `resolve_version(requested: str, versions: Dict[str, List[Type]]) -> Optional[List[Type]]`
  - `requested`: The version string requested by the consumer (e.g. `"28.16"`, `"v2"`, `"latest"`)
  - `versions`: The `VERSIONS` dict from a file class (keys are version strings, values are component type lists)
  - Returns: The component list for the resolved version, or `None` if `requested` is lower than all available keys

### Outputs/Behavior

- `resolve_version("v1", {"v1": [A], "v2": [B]})` returns `[A]`
- `resolve_version("v1.5", {"v1": [A], "v2": [B]})` returns `[A]` (v1.5 >= v1, v1.5 < v2)
- `resolve_version("v3", {"v1": [A], "v2": [B]})` returns `[B]` (v3 >= both)
- `resolve_version("v0", {"v1": [A], "v2": [B]})` returns `None` (v0 < v1)
- `resolve_version("28.16", {"28": [A], "28.16": [B]})` returns `[B]`
- `resolve_version("anything", {})` returns `None` (empty VERSIONS)

### Error Handling

- Empty `versions` dict: return `None` (no exception)
- No matching version (requested < all keys): return `None`
- The function does NOT raise exceptions -- callers decide what to do with `None`

## Acceptance Criteria

- [ ] Given `cfinterface/versioning.py` exists, when imported, then `SchemaVersion` and `resolve_version` are available
- [ ] Given a `VERSIONS` dict with keys `{"v1": [A], "v2": [B]}`, when `resolve_version("v1.5", versions)` is called, then `[A]` is returned (matches current `set_version` behavior)
- [ ] Given a `VERSIONS` dict with keys `{"v1": [A], "v2": [B]}`, when `resolve_version("v0", versions)` is called, then `None` is returned
- [ ] Given an empty `VERSIONS` dict `{}`, when `resolve_version("v1", {})` is called, then `None` is returned
- [ ] Given numeric-style keys `{"28": [A], "28.16": [B], "29.4.1": [C]}`, when `resolve_version("28.12", versions)` is called, then `[A]` is returned (lexicographic: "28.12" >= "28", "28.12" < "28.16")
- [ ] Given `cfinterface/__init__.py`, when `from cfinterface import SchemaVersion, resolve_version` is executed, then both are importable
- [ ] Given `SchemaVersion(key="v1", components=[A], description="initial")`, when accessed, then `.key == "v1"`, `.components == [A]`, `.description == "initial"`
- [ ] Given `SchemaVersion(key="v1", components=[A])`, when constructed without description, then `.description == ""`
- [ ] Given the existing test suite, when `pytest` is run, then all 331 existing tests still pass (no regressions)

## Implementation Guide

### Suggested Approach

1. Create `cfinterface/versioning.py` with:
   - `SchemaVersion = NamedTuple("SchemaVersion", [("key", str), ("components", List[Type]), ("description", str)])` using class-based `NamedTuple` form (matches `ColumnDef` pattern from epic-06)
   - Set `description` default to `""` via `__new__.__defaults__ = ("",)` or use the class-based form with default
   - `resolve_version()` function that replicates the `set_version` logic but returns the list instead of mutating class state
2. Add `from .versioning import SchemaVersion, resolve_version` to `cfinterface/__init__.py`
3. Add tests in `tests/test_versioning.py` (new file -- this is a new top-level module, not appended to an existing test file)

### Key Files to Modify

- `cfinterface/versioning.py` -- **new file**, home for `SchemaVersion` and `resolve_version`
- `cfinterface/__init__.py` -- add re-export line
- `tests/test_versioning.py` -- **new file**, unit tests

### Patterns to Follow

- `ColumnDef` in `cfinterface/components/tabular.py` is the reference for class-based `NamedTuple` with defaults (epic-06 learnings)
- Module uses one-line docstrings for private helpers; full numpydoc for public API classes (epic-01 convention)
- Type hints on all public functions (Python coding standard)
- No new dependencies -- use only `typing` and stdlib

### Pitfalls to Avoid

- Do NOT use `dataclass` for `SchemaVersion` -- `NamedTuple` is immutable and hashable by default, matching the `ColumnDef` precedent
- Do NOT change the version comparison semantic from lexicographic string `>=` -- inewave has 254+ subclasses relying on this exact behavior
- Do NOT create a `cfinterface/versioning/` subpackage -- a single file is sufficient for two exports
- Do NOT modify any file class (`registerfile.py`, `blockfile.py`, `sectionfile.py`) in this ticket -- that is ticket-025's scope

## Testing Requirements

### Unit Tests

- Test `resolve_version` with exact match, between-versions match, above-all-versions match, below-all-versions match, empty dict
- Test `resolve_version` with inewave-style numeric string keys (`"28"`, `"28.16"`, `"29.4.1"`)
- Test `SchemaVersion` construction with and without description
- Test `SchemaVersion` immutability (tuple)
- Test `SchemaVersion` equality

### Integration Tests

- Verify import from `cfinterface` top-level: `from cfinterface import SchemaVersion, resolve_version`

### E2E Tests (if applicable)

Not applicable.

## Dependencies

- **Blocked By**: None (epic-07 starts fresh; ticket-008 StorageType is already completed)
- **Blocks**: ticket-025, ticket-027

## Effort Estimate

**Points**: 2
**Confidence**: High
