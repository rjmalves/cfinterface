# ticket-015 Migrate Register/Block/Section prev/next to Computed Properties

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Convert the `previous` and `next` properties on `Register`, `Block`, and `Section` from stored linked-list pointers to computed properties that look up the element's position in its parent data container, eliminating the pointer storage overhead.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/components/register.py`, `cfinterface/components/block.py`, `cfinterface/components/section.py`, `cfinterface/data/registerdata.py`, `cfinterface/data/blockdata.py`, `cfinterface/data/sectiondata.py`
- **Key decisions needed**:
  - How to give each component a reference to its parent container (weak reference? direct reference? index-only?)
  - Whether to keep `previous`/`next` as settable properties for construction-time chain building, or make them read-only computed from container position
  - How to handle components that are not yet in any container (orphaned components)
- **Open questions**:
  - Does inewave code set `previous`/`next` directly, or only via `RegisterData.append()` / `add_before()` / `add_after()`?
  - What is the performance impact of O(n) `list.index()` for computing `previous`/`next`?
  - Should a component know its index in the parent container (cached) or look it up each time?

## Dependencies

- **Blocked By**: ticket-012, ticket-013, ticket-014
- **Blocks**: ticket-016

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
