# ticket-019 Update Line Class for Typed Dispatch

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Update the `Line` class to use typed dispatch based on `StorageType`, ensuring that `Line.read()` and `Line.write()` delegate to the correct repository without runtime `isinstance` checks on the data.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/components/line.py`, `cfinterface/adapters/components/line/repository.py`
- **Key decisions needed**: Whether `Line` becomes generic (`Line[str]` / `Line[bytes]`) or remains polymorphic with storage-based internal dispatch
- **Open questions**:
  - `Line` currently stores `storage: str` and creates the repository in `__generate_repository()`. Should the storage type determine the Line's generic parameter?
  - Does the `delimiter` parameter need separate typing for text vs binary (it can be `str | bytes`)?

## Dependencies

- **Blocked By**: ticket-017, ticket-018
- **Blocks**: ticket-020

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
