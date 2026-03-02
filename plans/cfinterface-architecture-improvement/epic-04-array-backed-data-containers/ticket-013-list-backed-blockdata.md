# ticket-013 Implement List-Backed BlockData Container

## Context

### Background

With the list-backed pattern established in ticket-012 for `RegisterData`, this ticket applies the same transformation to `BlockData`. The current `BlockData` class in `cfinterface/data/blockdata.py` is nearly identical to `RegisterData` in structure -- it uses `__root`/`__head` linked-list pointers, has O(n) `__len__`, and lacks indexed access. The only differences are the component type (`Block` instead of `Register`) and method names (`get_blocks_of_type` instead of `get_registers_of_type`).

### Relation to Epic

This is the second ticket in Epic 04. It directly follows the pattern established in ticket-012 for `RegisterData`, ensuring all three data containers are consistently list-backed. Once this and ticket-014 are complete, ticket-015 can convert `previous`/`next` to computed properties across all three component types.

### Current State

The file `cfinterface/data/blockdata.py` contains a `BlockData` class with:

- `__slots__ = ["__root", "__head"]` storing first/last pointers
- `__init__(self, root: Block)` setting both to the root
- `__iter__` walking `current.next` pointers
- `__len__` counting via iteration (O(n))
- `append`, `preppend`, `add_before`, `add_after` manipulating linked-list pointers
- `remove` unlinking pointers only (same bug as RegisterData -- `__root`/`__head` not updated)
- `of_type`, `get_blocks_of_type`, `remove_blocks_of_type` filtering by isinstance
- `first`/`last` properties returning `__root`/`__head`

The `BlockData` class is used by:

- `cfinterface/files/blockfile.py` -- `BlockFile.__init__` creates a default `BlockData(DefaultBlock())`, exposes `data` property
- `cfinterface/reading/blockreading.py` -- builds `BlockData` via `append()` only
- `cfinterface/writing/blockwriting.py` -- iterates via `for b in self.__data`

## Specification

### Requirements

1. Replace `__slots__ = ["__root", "__head"]` with `__slots__ = ["_items"]` where `_items` is a `List[Block]`
2. `__init__(self, root: Block)` initializes `_items = [root]`
3. `__iter__` yields from `_items`
4. `__len__` returns `len(self._items)` (O(1))
5. `__getitem__(self, idx)` returns `self._items[idx]` (new capability)
6. `append(b)` appends to `_items` and sets `previous`/`next` pointers on the new block and the previous tail
7. `preppend(b)` inserts at index 0 and sets `previous`/`next` pointers
8. `add_before(before, new)` inserts `new` at the index of `before`, updates `previous`/`next` pointers
9. `add_after(after, new)` inserts `new` after `after`, updates `previous`/`next` pointers
10. `remove(b)` removes `b` from `_items` by identity (`is`), patches adjacent pointers. Raise `ValueError` if not found
11. `of_type`, `get_blocks_of_type`, `remove_blocks_of_type` remain functionally identical
12. `first` returns `_items[0]`; `last` returns `_items[-1]`
13. `__eq__` compares `_items` lists directly
14. All pointer assertions in existing tests still pass

### Inputs/Props

- `root: Block` -- the initial block passed to `__init__`
- All mutation methods accept `Block` instances

### Outputs/Behavior

- Identical to ticket-012 pattern but for `Block` type
- `len()` is O(1), `__getitem__` is O(1)
- Pointers maintained on mutation for backward compatibility

### Error Handling

- `__getitem__` raises `IndexError` for out-of-bounds (default list behavior)
- `remove()` raises `ValueError` if element not found by identity

## Acceptance Criteria

- [ ] Given a `BlockData` with 1 root block, when `len()` is called, then it returns 1
- [ ] Given a `BlockData` with 10 appended blocks, when `len()` is called, then it returns 11 in O(1)
- [ ] Given a `BlockData` with 5 blocks, when `bd[2]` is called, then it returns the third block
- [ ] Given a `BlockData`, when `preppend(new)` is called, then `bd.first == new` and `new.next == old_first` and `old_first.previous == new`
- [ ] Given a `BlockData`, when `append(new)` is called, then `bd.last == new` and `new.previous == old_last` and `old_last.next == new`
- [ ] Given a `BlockData` with [root, b1], when `add_before(b1, new)` is called, then order is [root, new, b1] and `b1.previous == new`
- [ ] Given a `BlockData` with [root, b1], when `add_after(root, new)` is called, then order is [root, new, b1] and `root.next == new`
- [ ] Given a `BlockData` with [root, b1, b2], when `remove(b1)` is called, then order is [root, b2] and `root.next == b2` and `b2.previous == root`
- [ ] All 13 existing tests in `tests/data/test_blockdata.py` pass without modification
- [ ] All existing file-level block read/write tests pass

## Implementation Guide

### Suggested Approach

Follow the exact same pattern as the `RegisterData` rewrite from ticket-012, substituting `Block` for `Register` throughout.

1. Open `cfinterface/data/blockdata.py`
2. Replace `__slots__` with `["_items"]`
3. Rewrite `__init__` to `self._items: List[Block] = [root]`
4. Rewrite `__iter__` as `return iter(self._items)`
5. Rewrite `__len__` as `return len(self._items)`
6. Add `__getitem__` as `return self._items[idx]`
7. Rewrite `__eq__` to compare `self._items` with `o._items`
8. Rewrite `first`/`last` to return `self._items[0]`/`self._items[-1]`
9. Rewrite all mutation methods (`append`, `preppend`, `add_before`, `add_after`, `remove`) following the RegisterData pattern:
   - Use `_index_of` identity scan helper (same pattern as ticket-012)
   - Maintain `previous`/`next` pointers on blocks during mutation
10. Update `remove_blocks_of_type` guard from `b != self.__root` to `b is not self._items[0]`
11. Leave `of_type` and `get_blocks_of_type` functionally unchanged

**Note on BlockData.add_after**: The current `BlockData.add_after` has a slightly different null guard than `RegisterData.add_after`. Current code:

```python
if after == self.__head:
    self.__head = new
else:
    if after.next:
        after.next.previous = new
```

The `if after.next:` guard is present in BlockData but absent in RegisterData (which unconditionally accesses `after.next.previous`). The list-backed version handles this uniformly by checking `idx + 1 < len(self._items)` to determine if there is a successor element.

### Key Files to Modify

- `cfinterface/data/blockdata.py` -- full rewrite of class internals
- `tests/data/test_blockdata.py` -- add new tests for `__getitem__`

### Patterns to Follow

- Follow the exact same `_items` + `_index_of` pattern established in ticket-012 for `RegisterData`
- Use `_items` (single underscore) for the attribute name
- Keep all existing docstrings unchanged

### Pitfalls to Avoid

- Do NOT use `list.index()` -- use identity-based `_index_of` (same reason as ticket-012: `Block.__eq__` raises `NotImplementedError` on the base class, and `DummyBlock.__eq__` compares data)
- Do NOT forget to maintain `previous`/`next` pointers -- ticket-015 depends on them still working
- `Block.__eq__` on the base class raises `NotImplementedError` -- the `_index_of` identity scan avoids triggering this
- The guard in `remove_blocks_of_type` (`b != self.__root`) must use identity (`is not`) rather than equality to avoid triggering `Block.__eq__` which raises `NotImplementedError`

## Testing Requirements

### Unit Tests

Add the following tests to `tests/data/test_blockdata.py`:

1. `test_blockdata_getitem` -- create a BlockData with root + 3 appended blocks, verify `bd[0]` is root, `bd[3]` is last
2. `test_blockdata_getitem_negative` -- verify `bd[-1]` returns the last block
3. `test_blockdata_getitem_out_of_bounds` -- verify `bd[100]` raises `IndexError`
4. `test_blockdata_remove_updates_pointers` -- create [root, b1, b2, b3], remove b2, verify `b1.next == b3` and `b3.previous == b1`
5. `test_blockdata_remove_head` -- create [root, b1], remove b1, verify `bd.last is root` and `root.next is None`

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
