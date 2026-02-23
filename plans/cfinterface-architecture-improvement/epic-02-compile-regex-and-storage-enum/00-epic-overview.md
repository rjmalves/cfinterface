# Epic 02: Compile Regex Patterns and Introduce StorageType Enum

## Overview

This epic addresses two independent but related foundational improvements:

1. **Regex compilation**: All 7 `re.search()` calls in `cfinterface/adapters/components/repository.py` use raw string/bytes patterns on every invocation. These should be pre-compiled and cached for performance, especially in Register-based files where `matches()` is called on every line.

2. **StorageType enum**: The string literals `"TEXT"` and `"BINARY"` are threaded through the entire codebase as `storage: str` parameters. This is error-prone (typos, case sensitivity) and not type-safe. An enum replaces these strings while maintaining backward compatibility via factory functions that accept both.

## Goals

1. Pre-compile all regex patterns used in `matches()`, `begins()`, and `ends()` methods
2. Cache compiled patterns to avoid recompilation on repeated calls
3. Introduce `StorageType` enum with `TEXT` and `BINARY` members
4. Update all `factory()` functions to accept both `str` and `StorageType`
5. Update all internal usage to prefer `StorageType` while preserving `str` backward compat
6. Deprecate string-based storage parameter with warnings

## Scope

### In Scope

- cfinterface/adapters/components/repository.py (regex + enum)
- cfinterface/adapters/components/line/repository.py (enum)
- cfinterface/adapters/reading/repository.py (enum)
- cfinterface/adapters/writing/repository.py (enum)
- cfinterface/components/line.py (enum)
- cfinterface/components/register.py (enum)
- cfinterface/components/block.py (enum)
- cfinterface/components/section.py (enum)
- cfinterface/components/defaultregister.py (enum)
- cfinterface/files/registerfile.py, blockfile.py, sectionfile.py (enum)
- cfinterface/reading/\*.py (enum)
- cfinterface/writing/\*.py (enum)
- New: cfinterface/storage.py (StorageType enum definition)

### Out of Scope

- Changes to Field subclasses
- Changes to data containers
- Consumer code changes

## Tickets

| Ticket     | Title                                                             | Effort |
| ---------- | ----------------------------------------------------------------- | ------ |
| ticket-005 | Add regex pattern compilation and caching to component repository | 2      |
| ticket-006 | Create StorageType enum module                                    | 1      |
| ticket-007 | Update all factory functions to accept StorageType enum           | 2      |
| ticket-008 | Migrate internal storage parameter usage to StorageType           | 3      |
| ticket-009 | Add deprecation warnings for string-based storage parameters      | 1      |

## Success Criteria

- No raw `re.search(pattern, ...)` calls remain in the codebase
- `StorageType.TEXT` and `StorageType.BINARY` are usable throughout
- Existing code using `"TEXT"` and `"BINARY"` strings still works (with deprecation warning)
- All existing tests pass
- New benchmark test shows regex matching is faster with compilation
