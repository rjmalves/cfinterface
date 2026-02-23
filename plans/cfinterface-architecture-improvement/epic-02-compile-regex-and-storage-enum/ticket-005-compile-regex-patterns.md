# ticket-005 Add Regex Pattern Compilation and Caching to Component Repository

## Context

### Background

The `cfinterface/adapters/components/repository.py` module contains `TextualRepository` and `BinaryRepository` classes that use `re.search()` with raw string/bytes patterns on every call to `matches()`, `begins()`, and `ends()`. These methods are called once per line during file reading -- for a RegisterFile with 10,000 lines, `matches()` is called 10,000 times per register type. The patterns are class-level constants on Register/Block/Section subclasses and never change at runtime, making them ideal candidates for pre-compilation.

### Relation to Epic

This is the first ticket in Epic 02. It is independent of the StorageType enum work (tickets 006-009) and can be done in parallel. It targets the highest-impact performance improvement in the regex domain.

### Current State

In `cfinterface/adapters/components/repository.py`, there are 7 `re.search()` calls across 3 methods in 2 classes:

**BinaryRepository**:

- `matches()` (line 101): `re.search(pattern, line)` -- called per line per register type
- `matches()` (line 103): `re.search(pattern, line.decode("utf-8"))` -- fallback for str pattern with bytes line
- `begins()` (line 120): `re.search(pattern, line)` -- called per line per block type
- `ends()` (line 137): `re.search(pattern, line)` -- called per line per block type

**TextualRepository**:

- `matches()` (line 184): `re.search(pattern, line)` -- called per line per register type
- `begins()` (line 201): `re.search(pattern, line)` -- called per line per block type
- `ends()` (line 218): `re.search(pattern, line)` -- called per line per block type

The patterns come from class attributes like `Register.IDENTIFIER`, `Block.BEGIN_PATTERN`, `Block.END_PATTERN`. They are set once at class definition time and never modified during reading/writing.

## Specification

### Requirements

1. Create a module-level compiled pattern cache: `_pattern_cache: Dict[Union[str, bytes], re.Pattern] = {}`
2. Create a helper function `_compile(pattern: Union[str, bytes]) -> re.Pattern` that checks the cache first, compiles and stores on miss
3. Replace all 7 `re.search(pattern, line)` calls with `_compile(pattern).search(line)`
4. The cache is global to the module and persists for the process lifetime (patterns are class constants)
5. No API changes -- `matches()`, `begins()`, `ends()` signatures remain identical

### Inputs/Props

N/A -- internal refactoring, no public API change.

### Outputs/Behavior

Identical behavior to current implementation. The only difference is performance: repeated calls with the same pattern skip recompilation.

### Error Handling

If a pattern fails to compile (invalid regex), `re.compile()` raises `re.error` -- this is the same behavior as `re.search()` with an invalid pattern, so no change in error handling.

## Acceptance Criteria

- [ ] Given `cfinterface/adapters/components/repository.py`, when inspected, then there are ZERO bare `re.search()` calls
- [ ] Given `cfinterface/adapters/components/repository.py`, when inspected, then all pattern matching uses `_compile(pattern).search(line)`
- [ ] Given a `_pattern_cache` dict exists in the module, when `_compile("test")` is called twice, then the second call returns the same compiled pattern object (identity check with `is`)
- [ ] Given the existing tests in `tests/adapters/components/test_registerrepository.py`, when run, then they all pass
- [ ] Given the existing tests in `tests/adapters/components/test_blockrepository.py`, when run, then they all pass
- [ ] Given the full test suite, when `pytest tests/` is run, then all tests pass

## Implementation Guide

### Suggested Approach

Add the cache and helper at the top of the module, after the existing imports:

```python
from typing import Union, Dict, Type, IO
import re
from abc import ABC, abstractmethod

# Compiled regex pattern cache for matches/begins/ends.
# Patterns are class-level constants that never change at runtime,
# so caching them for the process lifetime is safe.
_pattern_cache: Dict[Union[str, bytes], "re.Pattern[Any]"] = {}


def _compile(pattern: Union[str, bytes]) -> "re.Pattern[Any]":
    """Compile and cache a regex pattern.

    :param pattern: The regex pattern to compile
    :type pattern: str | bytes
    :return: The compiled pattern
    :rtype: re.Pattern
    """
    compiled = _pattern_cache.get(pattern)
    if compiled is None:
        compiled = re.compile(pattern)
        _pattern_cache[pattern] = compiled
    return compiled
```

Then replace each `re.search(pattern, line)` with `_compile(pattern).search(line)`. For example:

**BinaryRepository.matches()** (lines 88-104):

```python
@staticmethod
def matches(pattern: Union[str, bytes], line: Union[str, bytes]) -> bool:
    if isinstance(pattern, bytes) and isinstance(line, bytes):
        return _compile(pattern).search(line) is not None
    elif isinstance(pattern, str) and isinstance(line, bytes):
        return _compile(pattern).search(line.decode("utf-8")) is not None
    return False
```

Apply the same transformation to `BinaryRepository.begins()`, `BinaryRepository.ends()`, `TextualRepository.matches()`, `TextualRepository.begins()`, `TextualRepository.ends()`.

### Key Files to Modify

- `cfinterface/adapters/components/repository.py`

### Patterns to Follow

- Module-level dict cache is the simplest approach (no need for `functools.lru_cache` since the key is just the pattern and we want to avoid the overhead of function call wrapping)
- Use `dict.get()` for thread-safe-enough reads (GIL protects simple dict operations)

### Pitfalls to Avoid

- Do NOT use `@functools.lru_cache` on the static methods themselves -- they take `line` as a parameter which changes every call, so caching at the method level would cache wrong results
- Do NOT pre-compile patterns at import time -- the patterns are defined on Register/Block/Section subclasses which may not be imported yet. Lazy compilation on first use is correct.
- Do NOT modify the method signatures or return types
- The `_compile()` function must handle BOTH `str` and `bytes` patterns since `BinaryRepository` uses both

## Testing Requirements

### Unit Tests

Add a new test file `tests/adapters/components/test_pattern_cache.py`:

```python
import re
from cfinterface.adapters.components.repository import _compile, _pattern_cache


def test_compile_caches_pattern():
    # Clear cache for isolation
    _pattern_cache.clear()
    p1 = _compile("test")
    p2 = _compile("test")
    assert p1 is p2  # Same object, not just equal


def test_compile_bytes_pattern():
    _pattern_cache.clear()
    p = _compile(b"test")
    assert isinstance(p, re.Pattern)
    assert p.search(b"this is a test") is not None


def test_compile_different_patterns():
    _pattern_cache.clear()
    p1 = _compile("foo")
    p2 = _compile("bar")
    assert p1 is not p2
    assert len(_pattern_cache) == 2
```

### Integration Tests

Run `pytest tests/` to verify all existing tests pass, especially:

- `tests/adapters/components/test_registerrepository.py`
- `tests/adapters/components/test_blockrepository.py`
- `tests/adapters/components/test_sectionrepository.py`
- `tests/components/test_register.py`
- `tests/components/test_block.py`

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None
- **Blocks**: None (independent of tickets 006-009)

## Effort Estimate

**Points**: 2
**Confidence**: High
