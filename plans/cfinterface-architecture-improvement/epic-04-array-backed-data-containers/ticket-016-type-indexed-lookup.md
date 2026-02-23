# ticket-016 Add Type-Indexed Lookup Optimization to Data Containers

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Add a secondary index (`Dict[Type, List[int]]`) to the data containers that maps component types to their indices in the backing list, making `of_type()` and `get_*_of_type()` O(k) where k is the number of matching elements instead of O(n) where n is total elements.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/data/registerdata.py`, `cfinterface/data/blockdata.py`, `cfinterface/data/sectiondata.py`
- **Key decisions needed**:
  - Whether to build the index lazily (on first `of_type()` call) or eagerly (on every `append()`/`remove()`)
  - Whether to invalidate the index on mutation or maintain it incrementally
  - Whether a base class approach (if adopted in ticket-013) simplifies adding the index
- **Open questions**:
  - What is the typical ratio of type-lookup calls to mutation calls? (If mutations are rare after construction, eager indexing is fine)
  - Should the index use `type(item)` or `isinstance` matching? (Current code uses `isinstance`, which matches subclasses)

## Dependencies

- **Blocked By**: ticket-015
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
