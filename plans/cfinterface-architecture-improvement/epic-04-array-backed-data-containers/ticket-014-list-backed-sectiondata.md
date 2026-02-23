# ticket-014 Implement List-Backed SectionData Container

## Context

### Background

This ticket completes the list-backed migration for the third and final data container class. With `RegisterData` (ticket-012) and `BlockData` (ticket-013) already converted, `SectionData` follows the same pattern. The current `SectionData` class in `cfinterface/data/sectiondata.py` is structurally identical to the other two containers -- linked-list pointers, O(n) `__len__`, no indexed access.

### Relation to Epic

This is the third ticket in Epic 04, completing the list-backed migration for all three data containers. With this ticket done, ticket-015 can safely convert `previous`/`next` from stored pointers to computed properties across all three component types, because all three containers will have a `_items` list that supports positional lookup.

### Current State

The file `cfinterface/data/sectiondata.py` contains a `SectionData` class with:

- `__slots__ = ["__root", "__head"]` storing first/last pointers
- `__init__(self, root: Section)` setting both to the root
- `__iter__` walking `current.next` pointers
- `__len__` counting via iteration (O(n))
- `append`, `preppend`, `add_before`, `add_after` manipulating linked-list pointers
- `remove` unlinking pointers only (same bug as RegisterData/BlockData)
- `of_type`, `get_sections_of_type`, `remove_sections_of_type` filtering by isinstance
- `first`/`last` properties returning `__root`/`__head`

The `SectionData` class is used by:

- `cfinterface/files/sectionfile.py` -- `SectionFile.__init__` creates a default `SectionData(DefaultSection())`, exposes `data` property
- `cfinterface/reading/sectionreading.py` -- builds `SectionData` via `append()` only
- `cfinterface/writing/sectionwriting.py` -- iterates via `for s in self.__data`

**Note on `remove_sections_of_type`**: Unlike `BlockData.remove_blocks_of_type`, the `SectionData.remove_sections_of_type` method uses the same dual-isinstance guard as `RegisterData.remove_registers_of_type`:

```python
if isinstance(filtered_sections, t) and isinstance(filtered_sections, Section):
    self.remove(filtered_sections)
```

This must be preserved in the rewrite.

## Specification

### Requirements

1. Replace `__slots__ = ["__root", "__head"]` with `__slots__ = ["_items"]` where `_items` is a `List[Section]`
2. `__init__(self, root: Section)` initializes `_items = [root]`
3. `__iter__` yields from `_items`
4. `__len__` returns `len(self._items)` (O(1))
5. `__getitem__(self, idx)` returns `self._items[idx]` (new capability)
6. `append(s)` appends to `_items` and sets `previous`/`next` pointers
7. `preppend(s)` inserts at index 0 and sets `previous`/`next` pointers
8. `add_before(before, new)` inserts `new` at the index of `before`, updates pointers
9. `add_after(after, new)` inserts `new` after `after`, updates pointers
10. `remove(s)` removes `s` from `_items` by identity, patches adjacent pointers. Raise `ValueError` if not found
11. `of_type`, `get_sections_of_type`, `remove_sections_of_type` remain functionally identical
12. `first` returns `_items[0]`; `last` returns `_items[-1]`
13. `__eq__` compares `_items` lists directly
14. All pointer assertions in existing tests still pass

### Inputs/Props

- `root: Section` -- the initial section passed to `__init__`
- All mutation methods accept `Section` instances

### Outputs/Behavior

- Identical to ticket-012/013 pattern but for `Section` type
- `len()` is O(1), `__getitem__` is O(1)
- Pointers maintained on mutation for backward compatibility

### Error Handling

- `__getitem__` raises `IndexError` for out-of-bounds
- `remove()` raises `ValueError` if element not found by identity

## Acceptance Criteria

- [ ] Given a `SectionData` with 1 root section, when `len()` is called, then it returns 1
- [ ] Given a `SectionData` with 10 appended sections, when `len()` is called, then it returns 11 in O(1)
- [ ] Given a `SectionData` with 5 sections, when `sd[2]` is called, then it returns the third section
- [ ] Given a `SectionData`, when `preppend(new)` is called, then `sd.first == new` and `new.next == old_first` and `old_first.previous == new`
- [ ] Given a `SectionData`, when `append(new)` is called, then `sd.last == new` and `new.previous == old_last` and `old_last.next == new`
- [ ] Given a `SectionData` with [root, s1], when `add_before(s1, new)` is called, then order is [root, new, s1] and `s1.previous == new`
- [ ] Given a `SectionData` with [root, s1], when `add_after(root, new)` is called, then order is [root, new, s1] and `root.next == new`
- [ ] Given a `SectionData` with [root, s1, s2], when `remove(s1)` is called, then order is [root, s2] and `root.next == s2` and `s2.previous == root`
- [ ] All 13 existing tests in `tests/data/test_sectiondata.py` pass without modification
- [ ] All existing file-level section read/write tests pass

## Implementation Guide

### Suggested Approach

Follow the exact same pattern as ticket-012 (`RegisterData`) and ticket-013 (`BlockData`), substituting `Section` for the component type.

1. Open `cfinterface/data/sectiondata.py`
2. Replace `__slots__` with `["_items"]`
3. Rewrite `__init__` to `self._items: List[Section] = [root]`
4. Rewrite `__iter__` as `return iter(self._items)`
5. Rewrite `__len__` as `return len(self._items)`
6. Add `__getitem__` as `return self._items[idx]`
7. Rewrite `__eq__` to compare `self._items` with `o._items`
8. Rewrite `first`/`last` to return `self._items[0]`/`self._items[-1]`
9. Rewrite all mutation methods following the established pattern:
   - Use `_index_of` identity scan helper
   - Maintain `previous`/`next` pointers on sections during mutation
10. Update `remove_sections_of_type` guard from `s != self.__root` to `s is not self._items[0]`
11. Leave `of_type` and `get_sections_of_type` functionally unchanged

### Key Files to Modify

- `cfinterface/data/sectiondata.py` -- full rewrite of class internals
- `tests/data/test_sectiondata.py` -- add new tests for `__getitem__`

### Patterns to Follow

- Follow the exact same `_items` + `_index_of` pattern established in tickets 012 and 013
- Use `_items` (single underscore) for the attribute name
- Keep all existing docstrings unchanged

### Pitfalls to Avoid

- Do NOT use `list.index()` -- use identity-based `_index_of` (same reason as tickets 012/013: `Section.__eq__` raises `NotImplementedError` on the base class)
- Do NOT forget to maintain `previous`/`next` pointers -- ticket-015 depends on them still working
- `Section.__eq__` on the base class raises `NotImplementedError` -- the `_index_of` identity scan avoids triggering this
- The guard in `remove_sections_of_type` must use identity (`is not`) to avoid triggering `Section.__eq__`
- The `remove_sections_of_type` method has the same dual-isinstance guard as `RegisterData.remove_registers_of_type`: `isinstance(filtered_sections, t) and isinstance(filtered_sections, Section)`. Preserve this pattern.

## Testing Requirements

### Unit Tests

Add the following tests to `tests/data/test_sectiondata.py`:

1. `test_sectiondata_getitem` -- create a SectionData with root + 3 appended sections, verify `sd[0]` is root, `sd[3]` is last
2. `test_sectiondata_getitem_negative` -- verify `sd[-1]` returns the last section
3. `test_sectiondata_getitem_out_of_bounds` -- verify `sd[100]` raises `IndexError`
4. `test_sectiondata_remove_updates_pointers` -- create [root, s1, s2, s3], remove s2, verify `s1.next == s3` and `s3.previous == s1`
5. `test_sectiondata_remove_head` -- create [root, s1], remove s1, verify `sd.last is root` and `root.next is None`

### Integration Tests

- Run the full existing test suite (`pytest tests/`) to verify no regressions

### E2E Tests (if applicable)

Not applicable.

## Dependencies

- **Blocked By**: ticket-012 (establishes the pattern)
- **Blocks**: ticket-015

## Effort Estimate

**Points**: 2
**Confidence**: High
