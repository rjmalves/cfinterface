# ticket-019 Update Line Class for Typed Dispatch

## Context

### Background

The `Line` class in `cfinterface/components/line.py` is the central bridge between raw file data (`str` or `bytes`) and the field-level read/write operations. It holds a `_storage` attribute (a `Union[str, StorageType]`), creates a `TextualRepository` or `BinaryRepository` via `factory(self._storage)` in `__generate_repository()`, and delegates `read()` and `write()` to that repository. Currently, `Line.read()` accepts `Union[str, bytes]` and `Line.write()` returns `Union[str, bytes]`, even though the storage type is known at construction time and determines which branch will be taken. This ticket adds `@overload` signatures to `Line.read()` and `Line.write()` so that callers who know the storage type can get precise types, and also tightens the `delimiter` property type.

### Relation to Epic

This ticket is the middle layer between the repository-level type safety (ticket-018) and the component-level type safety (ticket-020). Once Line provides typed read/write, Register can propagate those types to its callers.

### Current State

- `cfinterface/components/line.py`:
  - `__init__` accepts `storage: Union[str, StorageType] = ""`, `delimiter: Optional[Union[str, bytes]] = None`
  - `read(self, line: Union[str, bytes]) -> List[Any]` -- delegates to `self._repository.read(line, self._delimiter)`
  - `write(self, values: List[Any]) -> Union[str, bytes]` -- delegates to `self._repository.write(values, self._delimiter)`
  - `storage` property getter returns `Union[str, StorageType]`, setter calls `__generate_repository()`
  - `delimiter` property getter returns `Optional[Union[str, bytes]]`
  - `__generate_repository` calls `factory(self._storage)` from `cfinterface/adapters/components/line/repository.py`

- After ticket-018, `factory()` has `@overload` signatures that return `Type[TextualRepository]` for TEXT and `Type[BinaryRepository]` for BINARY. However, since `Line.__generate_repository()` calls `factory(self._storage)` where `self._storage` is a runtime value, mypy cannot narrow the return type at the call site. The overload on `factory()` helps callers who pass literal values, but `Line` itself stores the result as `self._repository` which will remain typed as `Repository` (the base class).

- Tests in `tests/components/test_line.py` cover both textual and binary read/write, including delimiter-based reading.

## Specification

### Requirements

1. Add `@overload` signatures to `Line.read()`:
   - `read(self, line: str) -> List[Any]`
   - `read(self, line: bytes) -> List[Any]`
     The return type is `List[Any]` in both cases (the field values), but the overloads enable mypy to check that the caller passes the correct type for the storage mode.

2. Add `@overload` signatures to `Line.write()`:
   - `write(self, values: List[Any]) -> str` (when storage is textual)
   - `write(self, values: List[Any]) -> bytes` (when storage is binary)

   However, since `write()` does not take a `str`/`bytes` discriminator argument, mypy cannot distinguish the two overloads from the call signature alone. Therefore, the `write()` return type must remain `Union[str, bytes]`. Instead of overloading, add a more precise docstring and leave the return type as `Union[str, bytes]`.

   **Alternative approach (chosen)**: Since the `write()` return type depends on the _storage_ mode (not the argument type), and the storage is a runtime value, we cannot use `@overload` to narrow `write()`. Keep `write()` return type as `Union[str, bytes]`. The real benefit comes from `read()` overloads and from tightening the `_repository` attribute type annotation.

3. **Type-annotate `_repository`**: Explicitly annotate `self._repository` in `__init__` as `Union[TextualRepository, BinaryRepository]` instead of the current implicit `Repository` (inferred from `factory()` return). This does not change runtime behavior but gives mypy more information about available methods.

   Actually, since the abstract `Repository` base class already defines all methods needed, and the concrete types are determined at runtime, the most accurate annotation remains `Repository`. Keep it as `Repository`.

4. **Tighten `delimiter` type annotation**: The `delimiter` parameter and property should remain `Optional[Union[str, bytes]]` because the Line class does not know at class definition time whether it is textual or binary. No change here.

5. **Add `@overload` to `Line.read()`** only, for the `str` vs `bytes` input distinction.

6. **Narrow `storage` property return type**: Change the `storage` property return type from `Union[str, StorageType]` to `Union[str, StorageType]` (no change -- it must remain wide because the empty string sentinel is valid).

7. **Add a module-level `_T` TypeVar** (or reuse from `typing`): Import `overload` and add the overloads for `read()`.

### Inputs/Props

- `Line.read(line)` -- `line` is `str` or `bytes`, unchanged.
- `Line.write(values)` -- `values` is `List[Any]`, unchanged.

### Outputs/Behavior

- Runtime behavior is identical.
- `Line.read("text")` is typed to return `List[Any]` and mypy can verify the argument is `str`.
- `Line.read(b"binary")` is typed to return `List[Any]` and mypy can verify the argument is `bytes`.
- `Line.write(values)` returns `Union[str, bytes]` (unchanged -- cannot be narrowed without a discriminator argument).

### Error Handling

- No changes to error handling.

## Acceptance Criteria

- [ ] Given `cfinterface/components/line.py`, when inspected, then `Line.read()` has `@overload` signatures for `str` and `bytes` inputs.
- [ ] Given `Line.read("text")`, when analyzed by mypy, then no type error is reported.
- [ ] Given `Line.read(b"binary")`, when analyzed by mypy, then no type error is reported.
- [ ] Given `Line.write()`, when inspected, then the return type remains `Union[str, bytes]` (cannot be narrowed).
- [ ] Given `pytest tests/`, when run, then all 268+ tests pass.
- [ ] Given `pytest tests/components/test_line.py`, when run, then all existing line tests pass.
- [ ] Given `ruff check cfinterface/components/line.py`, when run, then no lint errors are reported.

## Implementation Guide

### Suggested Approach

1. Add import of `overload` to `cfinterface/components/line.py`:

   ```python
   from typing import Any, List, Optional, Union, overload
   ```

2. Add `@overload` decorators to `Line.read()`:

   ```python
   @overload
   def read(self, line: str) -> List[Any]: ...

   @overload
   def read(self, line: bytes) -> List[Any]: ...

   def read(self, line: Union[str, bytes]) -> List[Any]:
       """
       Reads a line for extracting information following
       the given fields.

       :param line: The line to be read
       :type line: str | bytes
       :return: The extracted values, in order
       :rtype: List[Any]
       """
       return self._repository.read(line, self._delimiter)
   ```

3. Keep `Line.write()` signature as-is (return `Union[str, bytes]`). No overloads possible since the discriminator is the storage mode, not an argument type.

4. Run `pytest tests/` and `ruff check cfinterface/components/line.py`.

### Key Files to Modify

- `cfinterface/components/line.py` -- the only file modified in this ticket

### Patterns to Follow

- Follow the `@overload` pattern from ticket-017 (`Field.read()`).
- Keep the implementation signature using `Union[str, bytes]` for the line parameter.

### Pitfalls to Avoid

- Do NOT try to make `Line` generic over `str`/`bytes` (e.g., `Line[str]`) -- the storage type is a runtime value passed to `__init__`, and making `Line` generic would break the 254+ downstream subclasses that construct `Line(fields, storage="TEXT")` at class level (e.g., `Register.LINE = Line([])`). Class-level `LINE` attributes would need to become `Line[str]` which is a breaking change.
- Do NOT change the `write()` return type to `str` or `bytes` -- it depends on the storage mode and callers pass only `values`, not a typed line argument.
- Do NOT change `__generate_repository()` -- it works correctly at runtime.
- Do NOT add type annotations that conflict with the `storage=""` empty-string sentinel (which triggers the TextualRepository fallback).

## Testing Requirements

### Unit Tests

- Append to `tests/components/test_line.py`:
  - Test that `Line([]).read("")` returns an empty list (already exists as `test_line_read_no_fields`, just verify no regression).
  - Test that `Line(fields, storage="BINARY").read(b"hello, world!")` returns the correct values (already exists as `test_line_read_with_fields_binary`).
  - Confirm that the overloads do not break existing tests by running the full line test file.

### Integration Tests

- Run the full test suite (`pytest tests/`) to confirm no regressions.

### E2E Tests (if applicable)

- Not applicable.

## Dependencies

- **Blocked By**: ticket-017, ticket-018
- **Blocks**: ticket-020

## Effort Estimate

**Points**: 1
**Confidence**: High
