# ticket-016 Add Type-Indexed Lookup Optimization to Data Containers

## Context

### Background

After tickets 012-015, all three data containers use a `_items: List[...]` backing store with computed `previous`/`next` properties. The `of_type(t)` method and its dependents (`get_*_of_type`, `remove_*_of_type`) iterate through the entire `_items` list doing `isinstance(item, t)` checks, making them O(n) where n is total elements. For register files with thousands of elements and only a few types of interest, this is wasteful.

This ticket adds a secondary index -- `Dict[Type, List[int]]` -- that maps each concrete component type to a list of indices into `_items` where instances of that type appear. The `of_type` generator can then iterate only over matching indices, making lookups O(k) where k is the number of matching elements.

### Relation to Epic

This is the fifth and final ticket in Epic 04. It is an optimization layer on top of the list-backed containers completed in tickets 012-015. It does not change any public API -- it only makes existing operations faster.

### Current State

After tickets 012-015, the data containers have:

- `__slots__ = ["_items"]` with `_items: List[...]` as the backing store
- `_refresh_indices(start)` that sets `_container` and `_index` on elements after mutations
- `of_type(t)` iterates all `_items` and yields those passing `isinstance(item, t)`
- `get_*_of_type(t, **kwargs)` calls `of_type(t)` then filters by kwargs
- `remove_*_of_type(t, **kwargs)` calls `get_*_of_type` then removes matches

The reading classes (`RegisterReading`, `BlockReading`, `SectionReading`) build containers by appending one element at a time. The `_as_df` method on `RegisterFile` calls `list(self.data.of_type(register_type))`. These are the primary consumers of `of_type`.

## Specification

### Requirements

1. Add a `_type_index: Dict[Type, List[int]]` attribute to all three data container classes
2. Update `__slots__` from `["_items"]` to `["_items", "_type_index"]`
3. Initialize `_type_index` in `__init__` with the root element's type: `{type(root): [0]}`
4. Maintain the index incrementally on mutation operations:
   - `append(item)`: add `len(_items) - 1` to `_type_index[type(item)]`
   - `preppend(item)`: rebuild the full index (since all indices shift)
   - `add_before(before, new)`: rebuild the full index (since indices after insertion point shift)
   - `add_after(after, new)`: rebuild the full index (since indices after insertion point shift)
   - `remove(item)`: rebuild the full index (since indices after removal point shift)
5. Add a private `_rebuild_type_index()` method that reconstructs the entire index from `_items`
6. Update `of_type(t)` to use the type index with `isinstance` matching:
   - Iterate all type keys in `_type_index`, for each key where `issubclass(key, t)`, yield elements at those indices
   - This preserves the current `isinstance` semantics (matching subclasses)
   - Maintain insertion order: yield elements in ascending index order across all matching type keys
7. `get_*_of_type` and `remove_*_of_type` are unchanged -- they already call `of_type`

### Design Decisions

**Eager vs lazy indexing**: The index is maintained eagerly (rebuilt on every mutation) rather than lazily (built on first `of_type` call). Rationale: file reading is the dominant pattern -- elements are appended one by one during reading, and `of_type` is called many times afterward. Eager indexing during `append` is O(1) amortized (just append to a list). Rebuild is only needed for `preppend`, `add_before`, `add_after`, and `remove`, which are rare construction-time operations.

**`type(item)` vs `isinstance` for indexing**: The index maps `type(item)` (exact type) to indices. Lookup in `of_type(t)` iterates all keys and checks `issubclass(key, t)` to preserve the current `isinstance` semantics. This means if you have a class hierarchy `Register -> DummyRegister -> SpecialRegister`, calling `of_type(DummyRegister)` will find both `DummyRegister` and `SpecialRegister` instances.

**Optimization for `append`**: Since `append` is the most common mutation (called once per element during file reading), it should NOT trigger a full rebuild. Instead, it does:

```python
t = type(item)
if t not in self._type_index:
    self._type_index[t] = []
self._type_index[t].append(len(self._items) - 1)
```

This is O(1) amortized.

### Inputs/Props

No changes to the public API. All method signatures remain identical.

### Outputs/Behavior

- `of_type(t)` returns the same elements in the same order as before
- `get_*_of_type(t, **kwargs)` returns the same results as before
- `remove_*_of_type(t, **kwargs)` has the same effect as before
- Performance: `of_type(t)` is now O(k + m) where k is matching elements and m is number of distinct types, instead of O(n) where n is total elements

### Error Handling

No new error conditions. The type index is an internal optimization invisible to callers.

## Acceptance Criteria

- [ ] Given a `RegisterData` with 100 DummyRegisters and 100 DefaultRegisters, when `of_type(DummyRegister)` is called, then it returns exactly 100 elements (correctness)
- [ ] Given a `RegisterData` with 100 DummyRegisters and 100 DefaultRegisters, when `of_type(Register)` is called, then it returns all 200 elements (base class matching via issubclass)
- [ ] Given a `RegisterData`, when `append` is called 1000 times, then `_type_index` contains the correct entries without a full rebuild
- [ ] Given a `RegisterData` with [root, r1, r2], when `remove(r1)` is called, then `_type_index` is updated to exclude the removed element and indices are correct
- [ ] Given a `RegisterData`, when `preppend(new)` is called, then `_type_index` is rebuilt with correct shifted indices
- [ ] Given a `RegisterData`, when `of_type(t)` is called, then elements are yielded in the same order as they appear in `_items` (insertion order preserved)
- [ ] All existing tests in `tests/data/test_registerdata.py`, `test_blockdata.py`, `test_sectiondata.py` pass without modification
- [ ] All existing file-level read/write tests pass
- [ ] Same correctness criteria apply to `BlockData` and `SectionData`

## Implementation Guide

### Suggested Approach

1. Start with `RegisterData` (`cfinterface/data/registerdata.py`):

   a. Update `__slots__` to `["_items", "_type_index"]`

   b. In `__init__`, after `self._items = [root]`, add:

   ```python
   self._type_index: Dict[Type, List[int]] = {type(root): [0]}
   ```

   c. Add `_rebuild_type_index`:

   ```python
   def _rebuild_type_index(self) -> None:
       self._type_index = {}
       for i, item in enumerate(self._items):
           t = type(item)
           if t not in self._type_index:
               self._type_index[t] = []
           self._type_index[t].append(i)
   ```

   d. Update `append(r)`:
   After appending to `_items` and calling `_refresh_indices`, add:

   ```python
   t = type(r)
   if t not in self._type_index:
       self._type_index[t] = []
   self._type_index[t].append(len(self._items) - 1)
   ```

   e. Update `preppend`, `add_before`, `add_after`, `remove`:
   After modifying `_items` and calling `_refresh_indices`, call `self._rebuild_type_index()`

   f. Rewrite `of_type(t)`:

   ```python
   def of_type(self, t: Type[T]) -> Generator[T, None, None]:
       indices: List[int] = []
       for cls, idx_list in self._type_index.items():
           if issubclass(cls, t):
               indices.extend(idx_list)
       indices.sort()
       for idx in indices:
           yield self._items[idx]
   ```

2. Apply the same changes to `BlockData` and `SectionData`.

3. Run full test suite.

### Key Files to Modify

- `cfinterface/data/registerdata.py` -- add `_type_index`, `_rebuild_type_index`, update mutations and `of_type`
- `cfinterface/data/blockdata.py` -- same changes
- `cfinterface/data/sectiondata.py` -- same changes
- `tests/data/test_registerdata.py` -- add type-index-specific tests
- `tests/data/test_blockdata.py` -- add type-index-specific tests
- `tests/data/test_sectiondata.py` -- add type-index-specific tests

### Patterns to Follow

- Use `Dict[Type, List[int]]` from `typing` for the type annotation
- Use `type(item)` for indexing (exact type), `issubclass(key, t)` for lookup (matches subclasses)
- Maintain `_type_index` as a private attribute (single underscore, consistent with `_items`)

### Pitfalls to Avoid

- Do NOT use `isinstance` for the index keys -- the index maps exact types. Subclass matching is done at lookup time via `issubclass`. If you used `isinstance` for indexing, you would need to walk the MRO of every element on insertion.
- Do NOT forget to call `_rebuild_type_index` after `remove` -- the indices shift after element removal, so the existing entries in `_type_index` become stale.
- Do NOT forget the `indices.sort()` in `of_type` -- when collecting indices from multiple type buckets, they must be sorted to preserve insertion order.
- The `append` optimization (O(1) index update) only works because `append` adds to the end -- no existing indices shift. Do NOT attempt to apply the same optimization to `preppend` or `add_before`.
- The `of_type` generator is currently lazy (yields one at a time). The rewritten version collects all matching indices first, then yields. This is acceptable because `get_*_of_type` already materializes the full list. If laziness is important for very large containers, an alternative approach using `heapq.merge` could merge sorted index lists without collecting all first -- but this is premature optimization for the current use case.

## Testing Requirements

### Unit Tests

Add the following tests to `tests/data/test_registerdata.py`:

1. `test_registerdata_of_type_with_mixed_types` -- create a RegisterData with alternating DummyRegister and DefaultRegister instances, verify `of_type(DummyRegister)` returns only the DummyRegisters in insertion order
2. `test_registerdata_of_type_base_class` -- create a RegisterData with DummyRegister instances, verify `of_type(Register)` returns all of them (issubclass matching)
3. `test_registerdata_type_index_after_remove` -- create a RegisterData with [root, r1(DummyRegister), r2(DefaultRegister)], remove r1, verify `of_type(DummyRegister)` returns only root (if root is DummyRegister)
4. `test_registerdata_type_index_after_preppend` -- create a RegisterData, preppend a register, verify `of_type` returns correct results

Add equivalent tests to `tests/data/test_blockdata.py` and `tests/data/test_sectiondata.py`.

### Integration Tests

- Run the full existing test suite (`pytest tests/`) to verify no regressions

### E2E Tests (if applicable)

Not applicable.

## Dependencies

- **Blocked By**: ticket-015 (needs the `_refresh_indices` infrastructure and `_container`/`_index` on elements)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
