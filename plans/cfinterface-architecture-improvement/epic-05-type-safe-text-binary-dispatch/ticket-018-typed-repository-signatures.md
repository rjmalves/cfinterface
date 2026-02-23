# ticket-018 Separate TextualRepository and BinaryRepository Type Signatures

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Refine the type signatures of `TextualRepository` and `BinaryRepository` across all adapter layers (components, line, reading, writing) so that each class works exclusively with its respective type (`str` for textual, `bytes` for binary), eliminating `Union[str, bytes]` from their interfaces.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/adapters/components/repository.py`, `cfinterface/adapters/components/line/repository.py`, `cfinterface/adapters/reading/repository.py`, `cfinterface/adapters/writing/repository.py`
- **Key decisions needed**:
  - Whether the abstract `Repository` base class should be generic (`Repository[T]`) or keep `Union[str, bytes]`
  - How the factory function return type changes (currently returns `Type[Repository]`, should it return a union of specific types?)
- **Open questions**:
  - Does removing `Union` from the base class break any duck-typing patterns in consumers?
  - How does this interact with the `BinaryRepository.matches()` special case that accepts `str` pattern with `bytes` line?

## Dependencies

- **Blocked By**: ticket-017
- **Blocks**: ticket-019, ticket-020

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
