# ticket-025 Implement Instance-Level Version Binding for File Classes

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Replace the class-level `set_version()` pattern (which mutates shared class state and is not thread-safe) with instance-level version binding, where each file instance knows its schema version at construction time. This eliminates the race condition where `set_version()` affects all instances and removes the need for consumers to call `set_version()` before every `read()`.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/files/registerfile.py`, `cfinterface/files/blockfile.py`, `cfinterface/files/sectionfile.py`
- **Key decisions needed**:
  - Whether `read()` accepts a `version` parameter or whether the file class is instantiated with a version
  - How to deprecate the class-level `set_version()` while keeping it functional
  - Whether version binding affects the `REGISTERS`/`BLOCKS`/`SECTIONS` class attributes or uses instance attributes
- **Open questions**:
  - The current `set_version()` mutates `cls.REGISTERS = cls.VERSIONS[closest]`. How to make this instance-scoped without breaking subclass inheritance?
  - Should the `read()` classmethod become an instance method, or should a factory method handle version binding?

## Dependencies

- **Blocked By**: ticket-024
- **Blocks**: ticket-026

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
