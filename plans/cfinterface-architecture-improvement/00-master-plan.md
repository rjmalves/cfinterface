# Master Plan: cfinterface Architecture and Performance Improvement

## Executive Summary

This plan addresses architectural debt and performance bottlenecks in cfinterface, a Python file schema modeling framework used to parse/write dozens of legacy HPC file formats. The improvements are ordered by impact and risk: foundational dependency removal and performance wins first (pandas removal, regex compilation, storage enum), followed by structural improvements (data containers, type-safe dispatch), and finally consumer-facing features (generic tabular parser, schema versioning). All changes maintain backward compatibility with 254+ downstream file type implementations in inewave and sintetizador-newave.

## Goals & Non-Goals

### Goals

1. Remove the unnecessary pandas runtime dependency from cfinterface core (pandas is only used for `pd.isnull()`)
2. Pre-compile and cache regex patterns used for identifier/block pattern matching
3. Replace magic string `"TEXT"`/`"BINARY"` storage parameters with a type-safe enum
4. Optimize `FloatField._textual_write()` to eliminate the O(decimal_digits) precision loop
5. Replace linked list data containers with array-backed containers for O(1) `len()` and indexed access
6. Introduce type-safe text/binary dispatch eliminating `Union[str, bytes]` threading
7. Provide a generic tabular parser to reduce per-file custom DataFrame parsing in consumers
8. Add schema versioning support and batch operations API

### Non-Goals

- Modifying inewave or sintetizador-newave directly (cfinterface remains independent)
- Breaking backward compatibility without a migration path
- Adding streaming/chunked read support (deferred to future work after array-backed containers)
- Property accessor generation for consumer wrappers (separate future initiative)
- Typed `Section.data` generic parameter (separate future initiative, depends on Python version constraints)

## Architecture Overview

### Current State

```
cfinterface v1.8.3
  Field (base) --> FloatField, IntegerField, LiteralField, DatetimeField
    - All import pandas for pd.isnull() null detection
    - FloatField has O(n) textual write loop
  Line --> composed of Fields
    - Takes storage: str = "" parameter
  Register/Block/Section --> contain linked-list prev/next pointers
    - re.search() called per line without pre-compilation
    - "TEXT"/"BINARY" magic strings threaded through all APIs
  RegisterData/BlockData/SectionData --> linked list containers
    - O(n) __len__(), O(n) type filtering, no indexing
  RegisterFile/BlockFile/SectionFile --> high-level APIs
    - RegisterFile imports pandas for _as_df() helper
  adapters/ --> Repository pattern with factory("TEXT"/"BINARY") dispatch
```

### Target State

```
cfinterface v2.0.0
  Field (base) --> FloatField, IntegerField, LiteralField, DatetimeField
    - Native _is_null() helper using math.isnan/numpy, zero pandas dependency
    - FloatField uses direct format string, no precision loop
  StorageType enum --> TEXT, BINARY (replaces magic strings)
  Line --> composed of Fields, uses StorageType
  Register/Block/Section --> contain index into parent container (no linked-list pointers)
    - Compiled regex patterns cached at class level
  RegisterData/BlockData/SectionData --> list-backed containers
    - O(1) len(), indexed access, type-indexed lookups
  RegisterFile/BlockFile/SectionFile --> high-level APIs
    - pandas import deferred to _as_df() method only (optional dependency)
    - GenericTabularParser mixin for DataFrame construction
    - Schema versioning with explicit contracts
  adapters/ --> Repository pattern with StorageType enum dispatch
```

### Key Design Decisions

1. **pandas becomes optional**: Move pandas to optional dependency. Use `math.isnan()` + type checking for null detection in fields. The `_as_df()` method in RegisterFile keeps pandas but imports lazily.
2. **StorageType enum is additive**: The enum is introduced alongside the existing string API. Factory functions accept both `str` and `StorageType` during migration. The string API is deprecated but not removed.
3. **Array-backed containers preserve API**: `RegisterData`, `BlockData`, `SectionData` switch from linked lists to `list` internally. The `previous`/`next` properties on Register/Block/Section become computed from the parent container rather than stored pointers. The public API (`append`, `preppend`, `of_type`, `get_*_of_type`) is preserved.
4. **Regex compilation is transparent**: Patterns are compiled lazily at first use and cached as class attributes. No API change required.

## Technical Approach

### Tech Stack

- Python >=3.10, numpy >=2.0.0
- pandas >=2.2.3 (moved to optional dependency)
- pytest, ruff, mypy (dev)

### Component/Module Breakdown

| Epic | Component                                                   | Files Modified | Risk   |
| ---- | ----------------------------------------------------------- | -------------- | ------ |
| 1    | Field subclasses, pyproject.toml                            | 6 files        | Low    |
| 2    | adapters/components/repository.py, all storage string sites | 15 files       | Low    |
| 3    | FloatField.\_textual_write()                                | 1 file         | Low    |
| 4    | data/\*.py, Register/Block/Section prev/next                | 9 files        | Medium |
| 5    | adapters/_, components/_, type annotations                  | 15 files       | Medium |
| 6    | New module: cfinterface/parsers/                            | 3-5 new files  | Medium |
| 7    | files/\*.py, new module: cfinterface/versioning/            | 5-8 files      | Medium |

### Data Flow

```
File on disk
  --> ReadingRepository (opens file, manages IO)
    --> Reading class (dispatches lines to Register/Block/Section)
      --> Component.read(file, storage) (reads fields from line)
        --> Field.read(line) (extracts typed value from line slice)
          --> Data container stores components
            --> File class exposes data to consumer
```

### Testing Strategy

- Every ticket includes unit tests for the specific change
- Regression tests: run full existing test suite after each ticket
- Performance benchmarks: add pytest-benchmark fixtures for regex matching, field write, data container operations
- Integration validation: verify inewave test suite still passes (manual step at epic boundaries)

## Phases & Milestones

| Phase | Epic                                     | Duration  | Milestone                                                                        |
| ----- | ---------------------------------------- | --------- | -------------------------------------------------------------------------------- |
| 1     | Epic 1: Remove pandas dependency         | 1 week    | pandas is optional, all field tests pass without pandas installed                |
| 1     | Epic 2: Compile regex + StorageType enum | 1-2 weeks | All re.search() calls use compiled patterns, StorageType enum in place           |
| 2     | Epic 3: Optimize FloatField write        | 3-5 days  | FloatField.\_textual_write() uses direct formatting, benchmarks show improvement |
| 2     | Epic 4: Array-backed data containers     | 2-3 weeks | LinkedList replaced with list, O(1) len(), existing API preserved                |
| 3     | Epic 5: Type-safe text/binary dispatch   | 2-3 weeks | Union[str, bytes] eliminated from core APIs, adapters use StorageType            |
| 4     | Epic 6: Generic tabular parser           | 2-3 weeks | Reusable tabular parsing for consumers, reduces boilerplate                      |
| 4     | Epic 7: Schema versioning + batch ops    | 2-3 weeks | Version contracts, bulk read API                                                 |

## Risk Analysis

| Risk                                                      | Impact | Mitigation                                                                                                |
| --------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------- |
| Breaking 254+ downstream file types                       | High   | Backward-compatible changes only; deprecation before removal; string API preserved alongside enum         |
| pandas removal breaks consumers that pass NaN values      | Medium | The \_is_null() function handles numpy NaN, float NaN, and None; comprehensive test coverage              |
| Linked list to array migration changes iteration behavior | Medium | Preserve exact API surface; comprehensive tests for edge cases (concurrent modification during iteration) |
| Regex compilation overhead at import time                 | Low    | Lazy compilation on first use, not at class definition time                                               |

## Success Metrics

1. `pytest` passes with 100% of existing tests after each epic
2. pandas is no longer in `dependencies` (moved to `[project.optional-dependencies]`)
3. No `re.search()` calls with raw string patterns remain
4. `len(RegisterData)` is O(1) instead of O(n)
5. FloatField write benchmark shows measurable improvement
6. All `"TEXT"`/`"BINARY"` string literals replaced with `StorageType.TEXT`/`StorageType.BINARY`
