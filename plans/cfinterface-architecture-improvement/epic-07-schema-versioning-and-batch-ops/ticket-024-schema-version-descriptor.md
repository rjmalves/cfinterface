# ticket-024 Design SchemaVersion Descriptor and Registry

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Design and implement a `SchemaVersion` system that replaces the current `VERSIONS: Dict[str, List[Type[Register]]]` class attribute with an explicit, self-documenting schema version descriptor. Each version entry should declare what components (registers/blocks/sections) are included, what changed from the previous version, and the version string format.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/versioning/__init__.py` (new module), `cfinterface/versioning/schema.py` (new)
- **Key decisions needed**:
  - Whether versions use semantic versioning or arbitrary string keys (current system uses arbitrary strings like `"v29.0"`)
  - Whether `SchemaVersion` is a dataclass, named tuple, or class with validation
  - How to handle the `closest_version` resolution logic (currently duplicated in all 3 file classes)
- **Open questions**:
  - Should the version registry be global or per-file-class?
  - Should version descriptors carry metadata about what changed (for migration guidance)?
  - How should this interact with the existing `VERSIONS` dict pattern for backward compat?

## Dependencies

- **Blocked By**: ticket-008 (StorageType should be in place before adding more infrastructure)
- **Blocks**: ticket-025, ticket-027

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
