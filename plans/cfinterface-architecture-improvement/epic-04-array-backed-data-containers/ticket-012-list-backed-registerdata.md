# ticket-012 Implement List-Backed RegisterData Container

## Context

### Background

The current `RegisterData` class uses a linked list for internal storage. Each register holds `previous`/`next` pointers, and the container stores only `__root` (first) and `__head` (last) references. This means `__len__()` is O(n), `__iter__()` walks pointers, there is no indexed access, and each element carries two pointer references as overhead. For downstream packages like inewave that work with register files containing thousands of registers, `len()` is called frequently and its O(n) cost is measurable.

This ticket replaces the linked list with a Python `list` for internal storage, making `len()` O(1) and enabling O(1) indexed access via `__getitem__`. The `previous`/`next` pointer fields on `Register` instances are still maintained by the data container during mutation operations (append, prepend, add_before, add_after, remove) so that existing code reading `.previous`/`.next` on registers continues to work. Ticket-015 will later convert those stored pointers to computed properties.

### Relation to Epic

This is the first ticket in Epic 04 (Array-Backed Data Containers). It establishes the list-backed pattern that tickets 013 and 014 will replicate for `BlockData` and `SectionData`. The pattern established here -- `_items: List[Register]` internal storage, pointer maintenance on mutation, `__getitem__` support -- is the template for the other two containers.

### Current State

The file `cfinterface/data/registerdata.py` contains a `RegisterData` class with:

- `__slots__ = ["__root", "__head"]` storing first/last pointers
- `__init__(self, root: Register)` setting both `__root` and `__head` to the root
- `__iter__` walking `current.next` pointers
- `__len__` counting via iteration (O(n))
- `append`, `preppend`, `add_before`, `add_after` manipulating linked-list pointers
- `remove` unlinking pointers (but NOT updating `__root`/`__head` -- existing bug)
- `of_type`, `get_registers_of_type`, `remove_registers_of_type` filtering by isinstance
- `first`/`last` properties returning `__root`/`__head`

## Specification

### Requirements

1. Replace `__slots__ = ["__root", "__head"]` with `__slots__ = ["_items"]` where `_items` is a `List[Register]`
2. `__init__(self, root: Register)` initializes `_items = [root]`
3. `__iter__` yields from `_items` (preserves iteration order)
4. `__len__` returns `len(self._items)` (O(1))
5. `__getitem__(self, idx)` returns `self._items[idx]` (new capability, O(1))
6. `append(r)` appends to `_items` and sets `previous`/`next` pointers on the new register and the previous tail
7. `preppend(r)` inserts at index 0 of `_items` and sets `previous`/`next` pointers on the new register and the previous root
8. `add_before(before, new)` inserts `new` into `_items` at the index of `before`, shifting `before` right; updates `previous`/`next` pointers on the affected registers (new, before, and the register preceding before if any)
9. `add_after(after, new)` inserts `new` into `_items` at the index after `after`; updates `previous`/`next` pointers on the affected registers (new, after, and the register following after if any)
10. `remove(r)` removes `r` from `_items` by identity (`is`, not `==`); updates `previous`/`next` pointers on adjacent registers. Fix the existing bug where `__root`/`__head` were not updated on remove -- the list-backed version handles this automatically since `first`/`last` are computed from `_items[0]`/`_items[-1]`
11. `of_type`, `get_registers_of_type`, `remove_registers_of_type` remain functionally identical (iterate `_items` instead of pointer chain)
12. `first` property returns `_items[0]`; `last` property returns `_items[-1]`
13. `__eq__` compares element-by-element using `_items` directly
14. All existing pointer assertions in tests (`r1.previous == r2`, `r2.next == r1`) must still pass, because this ticket still maintains pointers on mutation

### Inputs/Props

- `root: Register` -- the initial register passed to `__init__`
- All mutation methods accept `Register` instances as before

### Outputs/Behavior

- `len()` returns in O(1)
- `__getitem__(i)` returns the i-th register in O(1)
- `first`/`last` return the first/last element from `_items`
- Iteration order is identical to insertion order
- `previous`/`next` pointers on registers are kept consistent with list position after every mutation

### Error Handling

- `__getitem__` raises `IndexError` for out-of-bounds access (default `list` behavior)
- `remove()` should use identity (`is`) scan of `_items` to find the element. If the element is not found (not `is`-identical to any element in the list), raise `ValueError` -- this is a new, more explicit failure mode vs. the current silent no-op for removed elements

## Acceptance Criteria

- [ ] Given a `RegisterData` with 1 root register, when `len()` is called, then it returns 1 without iterating
- [ ] Given a `RegisterData` with 10 appended registers, when `len()` is called, then it returns 11 in O(1)
- [ ] Given a `RegisterData` with 5 registers, when `rd[2]` is called, then it returns the third register
- [ ] Given a `RegisterData`, when `preppend(new)` is called, then `rd.first == new` and `new.next == old_first` and `old_first.previous == new`
- [ ] Given a `RegisterData`, when `append(new)` is called, then `rd.last == new` and `new.previous == old_last` and `old_last.next == new`
- [ ] Given a `RegisterData` with [root, r1], when `add_before(r1, new)` is called, then `_items` order is [root, new, r1] and `r1.previous == new` and `new.next == r1`
- [ ] Given a `RegisterData` with [root, r1], when `add_after(root, new)` is called, then `_items` order is [root, new, r1] and `root.next == new` and `new.previous == root`
- [ ] Given a `RegisterData` with [root, r1, r2], when `remove(r1)` is called, then `_items` is [root, r2] and `root.next == r2` and `r2.previous == root`
- [ ] Given a `RegisterData`, when iterated, then elements come out in the same order as `_items`
- [ ] All 13 existing tests in `tests/data/test_registerdata.py` pass without modification
- [ ] All existing file-level read/write tests pass (the reading/writing classes only use `append()` and iteration)
- [ ] New tests for `__getitem__` and O(1) `__len__` are added

## Implementation Guide

### Suggested Approach

1. Open `cfinterface/data/registerdata.py`
2. Replace `__slots__ = ["__root", "__head"]` with `__slots__ = ["_items"]`
3. Rewrite `__init__` to `self._items: List[Register] = [root]`
4. Rewrite `__iter__` as `return iter(self._items)`
5. Rewrite `__len__` as `return len(self._items)`
6. Add `__getitem__` as `return self._items[idx]`
7. Rewrite `__eq__` to compare `self._items` with `o._items` (after the isinstance check, access the protected attribute directly since same class)
8. Rewrite `first` property as `return self._items[0]`
9. Rewrite `last` property as `return self._items[-1]`
10. Rewrite `append(r)`: set `self._items[-1].next = r`, `r.previous = self._items[-1]`, `r.next = None`, then `self._items.append(r)`
11. Rewrite `preppend(r)`: set `self._items[0].previous = r`, `r.next = self._items[0]`, `r.previous = None`, then `self._items.insert(0, r)`
12. Rewrite `add_before(before, new)`: find index of `before` in `_items` by identity scan, insert `new` at that index, then fix `previous`/`next` pointers for `new`, `before`, and the element before `new` (if any)
13. Rewrite `add_after(after, new)`: find index of `after` in `_items` by identity scan, insert `new` at index+1, then fix `previous`/`next` pointers for `new`, `after`, and the element after `new` (if any)
14. Rewrite `remove(r)`: find index of `r` in `_items` by identity scan, patch the `previous`/`next` pointers of adjacent elements, then `del self._items[idx]`
15. Leave `of_type`, `get_registers_of_type`, and `remove_registers_of_type` functionally unchanged -- they already iterate via `self` so they will use the new `__iter__`
16. In `remove_registers_of_type`, the guard `r != self.__root` should become `r is not self._items[0]` -- use identity check for consistency

**Identity scan helper**: for `add_before`, `add_after`, and `remove`, write a private `_index_of(self, item: Register) -> int` method that scans `_items` with `is` comparison. This avoids using `list.index()` which uses `==` (and `Register.__eq__` compares by data, so two registers with the same data would be confused). Example:

```python
def _index_of(self, item: Register) -> int:
    for i, r in enumerate(self._items):
        if r is item:
            return i
    raise ValueError("Register not found in container")
```

### Key Files to Modify

- `cfinterface/data/registerdata.py` -- full rewrite of class internals
- `tests/data/test_registerdata.py` -- add new tests for `__getitem__`, do NOT modify existing tests

### Patterns to Follow

- Use `_items` (single underscore) as the attribute name, not `__items`. The `_items` convention signals "protected, not part of public API" while avoiding Python's name mangling which would make it harder for ticket-015 to access from a computed property on Register. Using `__slots__` still prevents external access since there is no `_items` on the instance dict.
- Keep all existing docstrings unchanged -- the public API semantics are identical
- Use numpydoc-style docstrings for any new public methods (`__getitem__`)

### Pitfalls to Avoid

- Do NOT use `list.index()` for finding elements -- it uses `__eq__` which compares register data, not identity. Two different `DummyRegister(data=-1)` instances would match each other. Always use the `_index_of` identity scan.
- Do NOT forget to set `r.next = None` and `r.previous = None` on new elements before linking them -- leftover pointers from a previous container could cause bugs.
- Do NOT remove the pointer maintenance code (setting `.previous`/`.next`) -- ticket-015 depends on it still working. The tests assert on it.
- The `remove_registers_of_type` method in the current code guards `r != self.__root` to avoid removing the root. Translate this to `r is not self._items[0]` using identity. The semantic is: never remove the first element via this bulk removal method.
- The `__eq__` method currently accesses `o` as a `RegisterData` type after isinstance check. In the rewrite, access `o._items` directly -- this works because `_items` is a same-class attribute.

## Testing Requirements

### Unit Tests

Add the following tests to `tests/data/test_registerdata.py`:

1. `test_registerdata_getitem` -- create a RegisterData with root + 3 appended registers, verify `rd[0]` is root, `rd[1]` is first appended, `rd[3]` is last appended
2. `test_registerdata_getitem_negative` -- verify `rd[-1]` returns the last register
3. `test_registerdata_getitem_out_of_bounds` -- verify `rd[100]` raises `IndexError`
4. `test_registerdata_len_is_o1` -- create a RegisterData with 1000 registers, call `len()` and verify it returns 1001 (this is a correctness test, not a timing test -- O(1) is verified by code inspection)
5. `test_registerdata_remove_updates_pointers` -- create [root, r1, r2, r3], remove r2, verify `r1.next == r3` and `r3.previous == r1`
6. `test_registerdata_remove_head` -- create [root, r1], remove r1, verify `rd.last is root` and `root.next is None`
7. `test_registerdata_iteration_order` -- create root + 5 appended registers, verify iteration order matches insertion order

### Integration Tests

- Run the full existing test suite (`pytest tests/`) to verify no regressions in file reading/writing

### E2E Tests (if applicable)

Not applicable for this ticket.

## Dependencies

- **Blocked By**: None (can start after epic 03 is complete)
- **Blocks**: ticket-013, ticket-014, ticket-015

## Effort Estimate

**Points**: 3
**Confidence**: High
