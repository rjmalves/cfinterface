# Epic 04 Learnings: Array-Backed Data Containers

**Epic**: epic-04-array-backed-data-containers
**Tickets**: ticket-012 through ticket-016
**Date**: 2026-02-23

---

## Patterns Established

- **`_items: List[T]` backing store**: All three data containers (`RegisterData`, `BlockData`, `SectionData`) now store elements in a single Python `list` attribute `_items`. `__len__` delegates to `len(self._items)`, `__iter__` to `iter(self._items)`, and `first`/`last` to `_items[0]`/`_items[-1]`. This is the canonical pattern for any future container class in this codebase -- see `cfinterface/data/registerdata.py` lines 16-27.

- **Identity scan `_index_of`**: Element lookup for `add_before`, `add_after`, and `remove` uses an explicit identity scan (`r is item`) rather than `list.index()`. `list.index()` uses `__eq__`, which raises `NotImplementedError` on the base `Block` and `Section` classes, and would confuse equal-but-distinct `Register` instances. The pattern is a private `_index_of(self, item) -> int` method that raises `ValueError` if not found -- see `cfinterface/data/registerdata.py` lines 41-45.

- **`_container` / `_index` back-reference on components**: Each `Register`, `Block`, and `Section` carries two protected single-underscore attributes: `_container` (direct reference to the owning data container, or `None` for orphaned components) and `_index` (integer position in `_items`). These are set by the container's `_refresh_indices` helper and cleared on `remove`. The single-underscore convention is intentional -- double-underscore would name-mangle and prevent the data container from setting them by simple attribute assignment -- see `cfinterface/components/register.py` lines 17-24.

- **`_refresh_indices(start: int)` incremental update**: After every mutation (`append`, `preppend`, `add_before`, `add_after`, `remove`), the container calls `_refresh_indices(start)` to rewrite `_container` and `_index` on every element from `start` to end. For `append`, `start = len(_items) - 1` (only the new tail). For all other mutations, `start` is the insertion/removal index, requiring O(n - start) work. This design accepts O(n) worst-case for prepend/remove-first in exchange for O(1) for append, which is the dominant path during file reading -- see `cfinterface/data/registerdata.py` lines 36-39.

- **`_type_index: Dict[Type, List[int]]` secondary index**: A second slot `_type_index` maps each exact concrete type to the list of `_items` indices where instances of that type live. `of_type(t)` collects all lists whose key passes `issubclass(key, t)`, sorts the combined index list, and yields elements in insertion order. `append` updates the index in O(1); all other mutations call `_rebuild_type_index()` for a full O(n) rebuild -- see `cfinterface/data/registerdata.py` lines 47-53 and 124-139.

- **Fallback `__previous_fallback` / `__next_fallback` for orphaned components**: The `previous` and `next` property getters check `_container is not None` first; if in a container, the value is computed from position. If orphaned (`_container is None`), the value is read from the private `__previous_fallback` / `__next_fallback` slots. The setters always write to the fallback slots. This preserves backward compatibility for test code and user code that builds component chains manually without a data container -- see `cfinterface/components/register.py` lines 107-128.

- **Tickets 012-014 implemented together with 015-016 in a single pass**: Despite the plan ordering these as sequential tickets, the developer merged the list-backed storage (012-014), computed properties (015), and type index (016) into a single implementation. The final files never went through the intermediate state described in tickets 012-014 (where pointer maintenance still existed). This is an acceptable deviation since the end state is correct.

---

## Architectural Decisions

- **Direct reference for `_container`, not weakref**: The ticket explicitly chose a direct object reference over `weakref.ref()`. Rationale: components and their containers share the same lifetime in all normal usage; a weakref would add dereferencing boilerplate and make tests noisier. Rejected alternative: weakref approach.

- **Eager `_type_index` maintenance, not lazy**: The index is rebuilt on every mutation rather than built lazily on first `of_type` call. Rationale: file reading (which calls `append` once per element) is the dominant workload, and `append` does O(1) index update; lazy would add a dirty-flag check on every `of_type` call. Rejected alternative: lazy build with dirty flag.

- **`type(item)` for indexing, `issubclass` for lookup**: The type index stores exact types as keys. `of_type(t)` matches keys with `issubclass(key, t)`. This separates storage (compact, exact types only) from retrieval (polymorphic, matches hierarchy). Rejected alternative: indexing with `isinstance` traversal, which would require walking the MRO on insertion.

- **`indices.sort()` inside `of_type` to preserve insertion order**: When multiple type buckets contribute indices, the combined list must be sorted before yielding. Without the sort, elements from different types would be grouped by type rather than interleaved in insertion order. This is a correctness requirement, not a performance consideration -- see `cfinterface/data/registerdata.py` line 137.

- **Slots discipline maintained**: All three data containers use `__slots__ = ["_items", "_type_index"]`. All three component classes use `__slots__` with explicitly named entries including the new `_container`, `_index`, `__previous_fallback`, `__next_fallback` attributes. Python's name mangling for double-underscore attributes means the slots must be listed with their mangled names when accessed from outside the class -- but since these are only accessed inside the component class itself, the canonical double-underscore names work correctly.

---

## Files and Structures Created / Modified

- `cfinterface/data/registerdata.py` -- full rewrite: `_items` list, `_type_index`, `_refresh_indices`, `_index_of`, `_rebuild_type_index`, computed `first`/`last`, updated all mutation methods and `of_type`
- `cfinterface/data/blockdata.py` -- same rewrite as `registerdata.py` for `Block` type
- `cfinterface/data/sectiondata.py` -- same rewrite as `registerdata.py` for `Section` type
- `cfinterface/components/register.py` -- replaced `__previous`/`__next` slots with `_container`, `_index`, `__previous_fallback`, `__next_fallback`; computed `previous`/`next`/`is_first`/`is_last` properties
- `cfinterface/components/block.py` -- same slot and property changes as `register.py`
- `cfinterface/components/section.py` -- same slot and property changes as `register.py`
- `tests/data/test_registerdata.py` -- 16 new tests appended (getitem, len, remove-pointer, iteration, computed prev/next, type-index)
- `tests/data/test_blockdata.py` -- 12 new tests appended (matching registerdata pattern for Block)
- `tests/data/test_sectiondata.py` -- 12 new tests appended (matching registerdata pattern for Section)
- `tests/components/test_register.py` -- 1 new test `test_register_orphaned_prev_next_fallback` appended

---

## Conventions Adopted

- **`_items` (single underscore) for the backing list, `_type_index` (single underscore) for the secondary index**: Protected, not private. Single underscore signals "internal to the module/class family" without triggering name mangling. Any future data container must use these same names for consistency.

- **`_container` and `_index` are single-underscore on components** so the data container can write `item._container = self` and `item._index = i` without going through a setter or using mangled names.

- **`__previous_fallback` and `__next_fallback` are double-underscore on components** because they are truly private to the component class -- the data container never touches them, only the component's own property getters/setters use them.

- **`_refresh_indices` is called after every `_items` mutation**, never before. The call site pattern is always: modify `_items`, call `_refresh_indices(start)`, update `_type_index`. Do not reorder these steps.

- **`_index_of` raises `ValueError` on miss**, not returns `-1`. This makes programming errors (removing an element not in the container) fail loudly rather than silently corrupt the index.

- **Test assertions on computed neighbors use `is` (identity), not `==` (equality)**: The tests verify `r1.next is r2` rather than `r1.next == r2`. This is the correct style because the assertion is about object identity (same instance), not data equality. Do not change these to `==`.

---

## Surprises and Deviations

- **All five tickets implemented atomically**: The plan described a staged approach where tickets 012-014 would first add list backing while keeping pointer maintenance, and ticket-015 would then remove pointer maintenance. The actual implementation collapsed all five tickets into a single pass that never went through the intermediate state. The final code is correct and the end state matches what was specified -- the deviation was in the implementation process, not the result.

- **`remove_registers_of_type` / `remove_blocks_of_type` / `remove_sections_of_type` guard changed from `!=` to `is not`**: The plan explicitly required changing `r != self.__root` to `r is not self._items[0]`. This was done correctly. The reason is that `Block.__eq__` and `Section.__eq__` raise `NotImplementedError` on the base class, so `!=` would throw for those types. See `cfinterface/data/blockdata.py` line 181 and `cfinterface/data/sectiondata.py` line 182.

- **`SectionData.remove_sections_of_type` preserves the dual-isinstance guard**: Ticket-014 noted that `SectionData` has `isinstance(filtered_sections, t) and isinstance(filtered_sections, Section)` where `RegisterData` uses only `isinstance(filtered_sections, t)`. Looking at the final `sectiondata.py`, the guard is `isinstance(filtered_sections, t)` only (line 177), matching `registerdata.py`. The dual guard mentioned in the ticket was not preserved. This is a minor divergence from the ticket spec but functionally equivalent for all concrete Section subclasses.

- **`Block.__eq__` raises `NotImplementedError` on the base class**: This is a pre-existing design choice (not introduced in this epic). It means any test or code path that compares `Block` instances through the base class will raise. The `DummyBlock` and `DefaultBlock` test fixtures override `__eq__`, and the container's `__eq__` compares `Block` instances through the concrete type's `__eq__`. The `_index_of` identity scan avoids triggering `__eq__` entirely -- this must remain true for any future mutation helpers added to `BlockData`.

---

## Recommendations for Future Epics

- When adding a new data container class (if ever needed), follow the exact `_items` + `_type_index` + `_refresh_indices` + `_index_of` + `_rebuild_type_index` pattern from `cfinterface/data/registerdata.py`. Do not invent a new backing-store convention.

- Any new component class that participates in a data container must add `_container`, `_index`, `__previous_fallback`, `__next_fallback` to its `__slots__` and implement the `previous`/`next`/`is_first`/`is_last` computed properties following `cfinterface/components/register.py`.

- The `_type_index` is intentionally exposed as a single-underscore attribute and is directly tested in `tests/data/test_registerdata.py` (e.g., `assert rd._type_index[DefaultRegister] == [1]`). Future tests that verify index correctness should continue to access `_type_index` directly -- it is a protected but observable internal.

- Epic-05 (type-safe text/binary dispatch) touches `factory()` functions and `StorageType` -- it does not interact with `_items`, `_type_index`, or `_container`/`_index`. These two change surfaces are fully isolated.

- Epic-06 (generic tabular parser) may introduce new component or container types. Before creating any new container class, read `cfinterface/data/registerdata.py` in full -- it is the reference implementation for the container pattern.

- The `_refresh_indices` call after `remove` starts at the removal index (elements at lower indices are unaffected). Future developers adding a bulk-remove method must call `_refresh_indices` at the lowest removed index, not at index 0 -- calling from 0 is correct but wasteful.
