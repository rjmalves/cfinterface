# ticket-017 Design Typed Field Read/Write Protocol

## Context

### Background

The `Field` base class in `cfinterface/components/field.py` already defines separate abstract methods for textual and binary paths (`_textual_read`/`_binary_read`/`_textual_write`/`_binary_write`), but the public `read(line)` and `write(line)` methods accept `Union[str, bytes]` and branch on `isinstance(line, bytes)` at runtime. The `TypeVar("T", str, bytes)` declared at class level is used in the signatures of `read()` and `write()` but provides no actual type narrowing to callers -- mypy cannot infer whether `T` is `str` or `bytes` from usage context because it is a class-level TypeVar not bound to a Generic parameter. This ticket adds `typing.overload` decorators so that mypy can statically determine the return type based on the argument type, and also tightens the internal `write()` flow to eliminate the redundant second `isinstance` check on the produced value.

### Relation to Epic

This is the foundational ticket for Epic 05. All subsequent tickets (018, 019, 020) build on the type-level contract established here. By making `Field.read()` and `Field.write()` return precise types based on the input type, the entire call chain upward (Line -> Register -> File) can propagate those types without widening to `Union`.

### Current State

- `cfinterface/components/field.py` lines 34-50: `read(self, line: T) -> Any` with `isinstance(line, bytes)` branch.
- `cfinterface/components/field.py` lines 60-91: `write(self, line: T) -> T` with two `isinstance` branches -- one to pick the value, one to assemble the line. The second branch (lines 78-91) rechecks both `value` and `line` types even though the value type is fully determined by the first branch.
- `Field.T = TypeVar("T", str, bytes)` is declared at class level (line 13) -- this is an unconventional placement. The TypeVar should be module-level for `@overload` usage.
- All four subclasses (`FloatField`, `IntegerField`, `LiteralField`, `DatetimeField`) implement the four abstract methods with correct return types -- no changes needed in subclasses.
- The `_is_null` utility is imported in all subclasses from `cfinterface/_utils/__init__.py`.

## Specification

### Requirements

1. Move the `TypeVar("T", str, bytes)` from class-level `Field.T` to module-level `_T` in `cfinterface/components/field.py`.
2. Add `@overload` signatures for `Field.read()`:
   - `read(self, line: str) -> Any`
   - `read(self, line: bytes) -> Any`
3. Add `@overload` signatures for `Field.write()`:
   - `write(self, line: str) -> str`
   - `write(self, line: bytes) -> bytes`
4. Keep the implementation signatures using the TypeVar (`_T`) so that the runtime behavior is unchanged.
5. Simplify the `write()` implementation body to eliminate the redundant second `isinstance` check on the produced value. Since the `isinstance(line, bytes)` check already determines the code path, the value type is known.
6. Preserve the existing ValueError catch in `read()` that sets `self._value = None`.
7. Preserve the `line.ljust(self.ending_position)` padding behavior in `write()`.
8. Do NOT change any subclass files -- only `cfinterface/components/field.py` is modified.

### Inputs/Props

- `Field.read(line)` -- `line` is either `str` or `bytes`, unchanged.
- `Field.write(line)` -- `line` is either `str` or `bytes`, unchanged.

### Outputs/Behavior

- Runtime behavior is identical to the current implementation.
- mypy can now narrow: if `field.read("hello")` is called, mypy knows the return type is `Any`. If `field.write("hello")` is called, mypy knows the return type is `str`.
- The `write()` method body is simplified: the value production and line assembly are done in a single `isinstance(line, bytes)` branch rather than two separate checks.

### Error Handling

- No change to error handling. `ValueError` in `read()` still sets `_value = None` and returns `None`.
- The "else return line" fallback at line 91 of the current `write()` should become unreachable. It can be removed since the overloads guarantee `line` is either `str` or `bytes`.

## Acceptance Criteria

- [ ] Given `cfinterface/components/field.py`, when the module is inspected, then `_T = TypeVar("T", str, bytes)` is at module level and `Field.T` no longer exists.
- [ ] Given `Field.read()`, when mypy strict mode analyzes the file, then the `@overload` signatures are correctly detected and no mypy errors are reported for `field.py`.
- [ ] Given `Field.write()`, when called with a `str` line, then mypy infers the return type as `str` (verified by an inline type assertion comment in the test).
- [ ] Given `Field.write()`, when called with a `bytes` line, then mypy infers the return type as `bytes`.
- [ ] Given the simplified `write()` body, when the second `isinstance` check on `value` is removed, then all existing tests pass (no behavior change).
- [ ] Given the full test suite, when `pytest tests/` is run, then all 268+ tests pass.
- [ ] Given `ruff check cfinterface/components/field.py`, when run, then no lint errors are reported.

## Implementation Guide

### Suggested Approach

1. Move `TypeVar` to module level:

   ```python
   from typing import Any, Optional, Union, TypeVar, overload

   _T = TypeVar("_T", str, bytes)
   ```

   Remove `T = TypeVar("T", str, bytes)` from inside the `Field` class body.

2. Add `@overload` decorators above `read()`:

   ```python
   @overload
   def read(self, line: str) -> Any: ...

   @overload
   def read(self, line: bytes) -> Any: ...

   def read(self, line: _T) -> Any:
       # existing implementation unchanged
   ```

3. Add `@overload` decorators above `write()`:

   ```python
   @overload
   def write(self, line: str) -> str: ...

   @overload
   def write(self, line: bytes) -> bytes: ...

   def write(self, line: _T) -> _T:
       # simplified implementation
   ```

4. Simplify `write()` body. The current body has two layers of `isinstance` checks. Refactor to:

   ```python
   def write(self, line: _T) -> _T:
       if isinstance(line, bytes):
           value = self._binary_write()
           if len(line) < self.ending_position:
               line = line.ljust(self.ending_position)
           return (
               line[: self.starting_position]
               + value
               + line[self.ending_position :]
           )
       else:
           value = self._textual_write()
           if len(line) < self.ending_position:
               line = line.ljust(self.ending_position)
           return (
               line[: self.starting_position]
               + value
               + line[self.ending_position :]
           )
   ```

   This eliminates the second `isinstance(value, str) and isinstance(line, str)` check and the unreachable `else: return line` fallback.

5. Run `pytest tests/` and `ruff check cfinterface/components/field.py` to verify.

### Key Files to Modify

- `cfinterface/components/field.py` -- the only file modified in this ticket

### Patterns to Follow

- The `@overload` pattern is standard typing module usage. See Python docs for `typing.overload`.
- Module-level TypeVars follow PEP 484 convention (underscore-prefixed `_T` for private TypeVars).
- Do not change the `@abstractmethod` decorators on the four internal methods.

### Pitfalls to Avoid

- Do NOT remove the `_T` TypeVar from the implementation signature -- it is needed for type-checker inference on the implementation body.
- Do NOT change any subclass files -- the `_binary_read`, `_textual_read`, `_binary_write`, `_textual_write` signatures in subclasses are already correct.
- Do NOT rename the TypeVar to `T` at module level -- use `_T` to signal it is private and avoid clashing with the existing `Field.T` that may be referenced by downstream code. The old `Field.T` attribute should be removed entirely (it was never part of the public API; it was a class-level TypeVar which is unusual).
- The `ljust()` call on `line` is reassignment (`line = line.ljust(...)`) which works fine with strings and bytes since both are immutable. Do not change this pattern.

## Testing Requirements

### Unit Tests

- Append tests to `tests/components/test_field.py`:
  - Test that `Field` no longer has a `T` class attribute (i.e., `hasattr(Field, 'T')` is `False` or it no longer appears as a TypeVar).
  - Test that calling `field.write("")` on a concrete subclass (e.g., `LiteralField`) returns `str`.
  - Test that calling `field.write(b"")` on a concrete subclass returns `bytes`.
  - Test that `field.read("...")` and `field.read(b"...")` both work on concrete subclasses.

### Integration Tests

- Run the full test suite (`pytest tests/`) to confirm no regressions across all 268+ existing tests.

### E2E Tests (if applicable)

- Not applicable for this ticket.

## Dependencies

- **Blocked By**: ticket-008 (completed -- StorageType is in place)
- **Blocks**: ticket-018, ticket-019

## Effort Estimate

**Points**: 2
**Confidence**: High
