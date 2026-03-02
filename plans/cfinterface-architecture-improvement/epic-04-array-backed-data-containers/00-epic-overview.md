# Epic 04: Array-Backed Data Containers

## Overview

Replace the linked list implementation in `RegisterData`, `BlockData`, and `SectionData` with `list`-backed containers. The current linked list implementation has O(n) `__len__()`, O(n) `get_*_of_type()`, no indexed access, and high pointer overhead per element (each node stores `previous` and `next` references). For a RegisterFile with 10,000 registers, `len()` walks the entire list every time it is called.

The array-backed containers use a Python `list` internally, providing O(1) `len()`, O(1) indexed access, and better cache locality. The `previous`/`next` properties on Register/Block/Section become computed from the container index rather than stored pointers.

## Goals

1. Replace linked list with `list` internal storage in all three data container classes
2. Preserve the exact public API (`append`, `preppend`, `add_before`, `add_after`, `remove`, `of_type`, `get_*_of_type`, `remove_*_of_type`, `first`, `last`)
3. Add `__getitem__` for indexed access (new capability)
4. Migrate `previous`/`next` from stored pointers to computed properties
5. Add type-indexed lookup optimization for `of_type()` / `get_*_of_type()`

## Tickets

| Ticket     | Title                                                           | Effort |
| ---------- | --------------------------------------------------------------- | ------ |
| ticket-012 | Implement list-backed RegisterData container                    | 3      |
| ticket-013 | Implement list-backed BlockData container                       | 2      |
| ticket-014 | Implement list-backed SectionData container                     | 2      |
| ticket-015 | Migrate Register/Block/Section prev/next to computed properties | 3      |
| ticket-016 | Add type-indexed lookup optimization to data containers         | 2      |

## Success Criteria

- O(1) `len()` on all data containers
- All existing data container tests pass
- All existing reading/writing/file tests pass
- `previous`/`next` navigation still works on Register/Block/Section instances
- Benchmark shows improvement for `len()`, `of_type()`, `get_*_of_type()` operations
