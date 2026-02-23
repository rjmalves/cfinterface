# ticket-012 Implement List-Backed RegisterData Container

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Rewrite `RegisterData` in `cfinterface/data/registerdata.py` to use a Python `list` instead of a linked list for internal storage, providing O(1) `__len__()` and O(1) indexed access while preserving the complete existing public API.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/data/registerdata.py`, `tests/data/test_registerdata.py`
- **Key decisions needed**:
  - Whether to keep `__root` and `__head` as cached references or compute them from `_items[0]` and `_items[-1]`
  - How to handle `add_before()` and `add_after()` with O(n) list insertion (acceptable for construction-time operations)
  - Whether to also update the `Register` class's `previous`/`next` pointers in this ticket or defer to ticket-015
- **Open questions**:
  - Does any downstream code rely on the identity of `Register` objects within the linked list (pointer comparison)?
  - Are there concurrent modification patterns (iterating while appending) in inewave that would break with list-based storage?
  - Should `__getitem__` be added for indexed access as part of this ticket?

## Dependencies

- **Blocked By**: None (can start after epic 02 is complete)
- **Blocks**: ticket-013, ticket-014, ticket-015

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
