# ticket-015 Migrate Register/Block/Section prev/next to Computed Properties

## Context

### Background

After tickets 012-014, all three data containers (`RegisterData`, `BlockData`, `SectionData`) store their elements in a `_items: List[...]` and maintain `previous`/`next` pointers on each component during every mutation operation. This dual bookkeeping is a transitional state -- the stored pointers are now redundant because the element's position in `_items` fully determines its neighbors.

This ticket removes the stored `__previous`/`__next` attributes from `Register`, `Block`, and `Section`, and replaces them with computed properties that look up the element's container and index. This eliminates the per-element pointer overhead (2 references per element) and removes the pointer-maintenance code from all three data containers.

### Relation to Epic

This is the fourth ticket in Epic 04. It depends on all three list-backed container tickets (012-014) being complete. After this ticket, the data containers no longer need to maintain pointers on mutation, simplifying the code significantly. Ticket-016 (type-indexed lookup) can proceed independently after this, or in parallel.

### Current State

After tickets 012-014, the codebase is in this state:

**Component classes** (`Register`, `Block`, `Section`):

- Each has `__slots__ = ["__previous", "__next", "__data", ...]`
- `previous` and `next` are properties with getters and setters
- `is_first` returns `self.__previous is None`
- `is_last` returns `self.__next is None`
- `__init__` accepts `previous=None, next=None, data=None`

**Data container classes** (`RegisterData`, `BlockData`, `SectionData`):

- Each has `__slots__ = ["_items"]` with a `List[...]` backing store
- Each mutation method (`append`, `preppend`, `add_before`, `add_after`, `remove`) updates both `_items` and the `previous`/`next` pointers on affected components

**Test assertions** that check `r1.previous == r2` and `r2.next == r1` in data container tests currently pass because the data containers maintain the pointers.

**Component tests** in `tests/components/test_register.py`, `test_block.py`, `test_section.py` directly set `previous`/`next` on orphaned components (not in any container) and check `is_first`/`is_last`. These tests create components manually and wire them together without using a data container.

## Specification

### Requirements

#### 1. Add container back-reference to components

Each component needs to know which container it belongs to and at what index, so that `previous`/`next` can be computed.

**Approach**: Add a `_container` attribute (weak reference or direct reference) and a `_index` attribute to each component class. The data container sets these when an element is added and clears them when removed.

**Design decision**: Use direct reference (not weakref) for simplicity. The container and its elements have the same lifetime -- a component never outlives its container in normal usage. Use `None` for orphaned components (not in any container).

Add to `Register.__slots__`: replace `["__previous", "__next", "__data", "__identifier_field"]` with `["__data", "__identifier_field", "_container", "_index"]`

Add to `Block.__slots__`: replace `["__previous", "__next", "__data"]` with `["__data", "_container", "_index"]`

Add to `Section.__slots__`: replace `["__previous", "__next", "__data"]` with `["__data", "_container", "_index"]`

#### 2. Convert `previous`/`next` to computed properties

For `Register`:

```python
@property
def previous(self) -> "Register":
    if self._container is None or self._index == 0:
        return None
    return self._container._items[self._index - 1]

@property
def next(self) -> "Register":
    if self._container is None or self._index >= len(self._container._items) - 1:
        return None
    return self._container._items[self._index + 1]
```

Same pattern for `Block` and `Section`, substituting the appropriate types.

#### 3. Keep `previous`/`next` setters for backward compatibility

The component tests (`test_register_simple_chain_properties`, `test_block_simple_chain_properties`, `test_section_simple_chain_properties`) directly set `previous`/`next` on orphaned components. To maintain backward compatibility, keep the setters but have them operate on a fallback `__previous_fallback`/`__next_fallback` stored attribute that is only used when `_container is None`.

Updated approach for `previous` property:

```python
@property
def previous(self) -> "Register":
    if self._container is not None:
        if self._index == 0:
            return None
        return self._container._items[self._index - 1]
    return self.__previous_fallback

@previous.setter
def previous(self, b: "Register"):
    self.__previous_fallback = b
```

This means: if the component is in a container, `previous`/`next` are computed from position; if it is orphaned, they fall back to the stored value (legacy behavior).

Add `"_Register__previous_fallback"` and `"_Register__next_fallback"` to `Register.__slots__` (and equivalently for Block and Section). Use double-underscore for these so they are name-mangled and not accessible externally -- they are purely a backward-compatibility mechanism.

Updated `Register.__slots__`: `["__data", "__identifier_field", "_container", "_index", "__previous_fallback", "__next_fallback"]`

#### 4. Update `is_first`/`is_last`

```python
@property
def is_first(self) -> bool:
    if self._container is not None:
        return self._index == 0
    return self.__previous_fallback is None

@property
def is_last(self) -> bool:
    if self._container is not None:
        return self._index == len(self._container._items) - 1
    return self.__next_fallback is None
```

#### 5. Update `__init__` on all three component classes

Keep the `previous=None, next=None, data=None` signature for backward compatibility. Store `previous`/`next` into the fallback attributes. Initialize `_container = None` and `_index = 0`.

```python
def __init__(self, previous=None, next=None, data=None) -> None:
    self.__previous_fallback = previous
    self.__next_fallback = next
    self._container = None
    self._index = 0
    # ... rest of init
```

#### 6. Update data container mutation methods

In all three data containers, after inserting or removing an element from `_items`, call a private helper `_refresh_indices(start_idx)` that updates `_container` and `_index` on all elements from `start_idx` to the end of the list. Remove all `previous`/`next` pointer maintenance code.

```python
def _refresh_indices(self, start: int = 0) -> None:
    for i in range(start, len(self._items)):
        self._items[i]._container = self
        self._items[i]._index = i
```

For `append(r)`: `self._items.append(r)`, then `self._refresh_indices(len(self._items) - 1)`
For `preppend(r)`: `self._items.insert(0, r)`, then `self._refresh_indices(0)`
For `add_before(before, new)`: find index, `self._items.insert(idx, new)`, then `self._refresh_indices(idx)`
For `add_after(after, new)`: find index, `self._items.insert(idx + 1, new)`, then `self._refresh_indices(idx + 1)`
For `remove(r)`: find index, `del self._items[idx]`, set `r._container = None`, `r._index = 0`, then `self._refresh_indices(idx)`

#### 7. Update DefaultRegister, DefaultBlock, DefaultSection

These subclasses call `super().__init__(previous, next, data)` -- no changes needed if the base class `__init__` signature is preserved.

### Inputs/Props

No public API changes. The `previous`, `next`, `is_first`, `is_last` properties exist as before. The `__init__` signatures are unchanged.

### Outputs/Behavior

- `previous`/`next` return the correct neighbor based on container position
- Orphaned components (not in any container) still support `previous`/`next` via the fallback mechanism
- `is_first`/`is_last` work correctly for both in-container and orphaned components
- Pointer-maintenance code is removed from data containers

### Error Handling

- Accessing `previous` on the first element returns `None`
- Accessing `next` on the last element returns `None`
- Orphaned components default to `None` for `previous`/`next` (unless explicitly set via setter)

## Acceptance Criteria

- [ ] Given a `RegisterData` with [root, r1, r2], when `r1.previous` is accessed, then it returns `root` (computed from container position, not stored pointer)
- [ ] Given a `RegisterData` with [root, r1, r2], when `r2.next` is accessed, then it returns `None`
- [ ] Given a `RegisterData` with [root, r1, r2], when `root.is_first` is checked, then it returns `True`
- [ ] Given a `RegisterData` with [root, r1, r2], when `r2.is_last` is checked, then it returns `True`
- [ ] Given an orphaned `Register()`, when `r.previous` is accessed, then it returns `None`
- [ ] Given an orphaned `Register()` with `r.previous = other`, when `r.previous` is accessed, then it returns `other`
- [ ] Given a `RegisterData` with [root, r1, r2], when `r1` is removed, then `r1._container is None` and `root.next == r2` and `r2.previous == root`
- [ ] All existing data container tests in `tests/data/test_registerdata.py`, `test_blockdata.py`, `test_sectiondata.py` pass without modification
- [ ] All existing component tests in `tests/components/test_register.py`, `test_block.py`, `test_section.py` pass without modification (the orphaned-component chain tests use setters and check is_first/is_last)
- [ ] All existing file-level read/write tests pass
- [ ] No `previous`/`next` pointer maintenance code remains in the data container mutation methods (the containers only manipulate `_items`, `_container`, and `_index`)
- [ ] The `_REGISTER_PROPERTIES` list on `Register` still includes `"previous"` and `"next"` (used by `custom_properties`)

## Implementation Guide

### Suggested Approach

Work in this order:

1. **Update `Register` class** (`cfinterface/components/register.py`):
   - Update `__slots__` to `["__data", "__identifier_field", "_container", "_index", "__previous_fallback", "__next_fallback"]`
   - Update `__init__` to initialize `_container = None`, `_index = 0`, `__previous_fallback = previous`, `__next_fallback = next`
   - Rewrite `previous` property getter to check `_container` first, fall back to `__previous_fallback`
   - Keep `previous` setter to set `__previous_fallback`
   - Same for `next` property
   - Rewrite `is_first` and `is_last` to check `_container` first, fall back to `__previous_fallback is None`/`__next_fallback is None`

2. **Run component tests** to verify orphaned-component behavior still works: `pytest tests/components/test_register.py`

3. **Update `RegisterData`** (`cfinterface/data/registerdata.py`):
   - Add `_refresh_indices(self, start: int = 0)` method
   - In `__init__`, after `self._items = [root]`, call `self._refresh_indices(0)` to set `root._container = self` and `root._index = 0`
   - Rewrite all mutation methods to: modify `_items`, call `_refresh_indices`, and NOT touch `previous`/`next` pointers
   - In `remove`, after removing from `_items`, set `r._container = None` and `r._index = 0`

4. **Run data container tests**: `pytest tests/data/test_registerdata.py`

5. **Repeat steps 1-4 for `Block`/`BlockData` and `Section`/`SectionData`**

6. **Run full test suite**: `pytest tests/`

### Key Files to Modify

- `cfinterface/components/register.py` -- new slots, computed previous/next, fallback mechanism
- `cfinterface/components/block.py` -- same changes as register.py
- `cfinterface/components/section.py` -- same changes as register.py
- `cfinterface/data/registerdata.py` -- add `_refresh_indices`, remove pointer maintenance
- `cfinterface/data/blockdata.py` -- same changes as registerdata.py
- `cfinterface/data/sectiondata.py` -- same changes as registerdata.py

No new test files are needed -- existing tests cover all the behavior. Optionally add a few tests to explicitly verify the computed-from-container behavior.

### Patterns to Follow

- Use `_container` and `_index` as single-underscore attributes (protected, not private) so that the data container can set them directly without name mangling
- Use `__previous_fallback` and `__next_fallback` as double-underscore attributes (private, name-mangled) since they are internal to the component class
- The `_refresh_indices` method is a private helper on the data container, not part of the public API

### Pitfalls to Avoid

- Do NOT remove the `previous`/`next` setters -- the component tests set them directly on orphaned components. The setters must continue to work.
- Do NOT change the `__init__` signature -- `DefaultRegister`, `DefaultBlock`, `DefaultSection` all call `super().__init__(previous, next, data)`. The `previous` and `next` parameters must still be accepted and stored in the fallback attributes.
- When a component is removed from a container (`remove(r)`), set `r._container = None` so that subsequent `r.previous`/`r.next` accesses use the fallback (which will be `None` since the fallback is not updated post-removal).
- The `_REGISTER_PROPERTIES` list on `Register` includes `"previous"` and `"next"` -- do not remove these entries, they are used by `custom_properties` to exclude framework properties from user-defined property discovery.
- The `_refresh_indices` call on `append` only needs to refresh the newly added element (start = len - 1). For `preppend` and `add_before`, it must refresh from the insertion point to the end. For `remove`, it must refresh from the removal point to the end. This is O(n) in the worst case (prepend/remove-first), but these are construction-time operations and the cost is acceptable.

## Testing Requirements

### Unit Tests

Add the following tests to `tests/data/test_registerdata.py`:

1. `test_registerdata_computed_previous_next` -- create [root, r1, r2], verify `r1.previous is root` and `r1.next is r2` (using identity, not equality) and `root.previous is None` and `r2.next is None`
2. `test_registerdata_computed_after_remove` -- create [root, r1, r2], remove r1, verify `root.next is r2` and `r2.previous is root` and `r1._container is None`

Add equivalent tests to `tests/data/test_blockdata.py` and `tests/data/test_sectiondata.py`.

Add to `tests/components/test_register.py`:

3. `test_register_orphaned_prev_next_fallback` -- create a Register, set `r.previous = other`, verify `r.previous is other`; then do NOT add to container, verify it still works

### Integration Tests

- Run the full existing test suite (`pytest tests/`) to verify no regressions in file reading/writing

### E2E Tests (if applicable)

Not applicable.

## Dependencies

- **Blocked By**: ticket-012, ticket-013, ticket-014
- **Blocks**: ticket-016

## Effort Estimate

**Points**: 3
**Confidence**: High
