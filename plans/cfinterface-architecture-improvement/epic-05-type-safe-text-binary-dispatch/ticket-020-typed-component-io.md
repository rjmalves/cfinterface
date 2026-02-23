# ticket-020 Update Register/Block/Section for Typed IO Paths

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Update `Register`, `Block`, and `Section` classes so that their `read()` and `write()` methods use typed IO paths based on `StorageType`, eliminating the `storage: str` parameter threading and leveraging the typed dispatch infrastructure built in tickets 017-019.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/components/register.py`, `cfinterface/components/block.py`, `cfinterface/components/section.py`, `cfinterface/components/defaultregister.py`, `cfinterface/components/defaultblock.py`, `cfinterface/components/defaultsection.py`
- **Key decisions needed**:
  - Whether `storage` becomes a class-level attribute only (set once at definition) rather than a method parameter
  - How to handle `DefaultRegister` which currently checks `storage not in ["BINARY"]` at runtime
- **Open questions**:
  - Can `storage` be fully removed from method signatures if it is known at file/reading class level?
  - How does this interact with `Register.read()` which creates a new `Line` with `storage=storage` on every call?

## Dependencies

- **Blocked By**: ticket-019
- **Blocks**: None

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
