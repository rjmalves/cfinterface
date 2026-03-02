# ticket-020 Update Register/Block/Section for Typed IO Paths

## Context

### Background

The `Register`, `Block`, and `Section` component classes are the top-level components that consumers subclass to define file formats. They each accept a `storage: Union[str, StorageType]` parameter in their `read()` and `write()` methods (Register explicitly, Block/Section via `*args, **kwargs`). The `storage` parameter is threaded down through the call chain: File -> Reading/Writing -> Component.read()/write(). After tickets 017-019 established type-safe overloads on Field, Repository, and Line, this ticket adds `@overload` signatures to the component-level `read()`/`write()` and `matches()`/`begins()`/`ends()` class methods, tightening the type annotations for the `storage` parameter and the `line` parameter where applicable.

### Relation to Epic

This is the final ticket in Epic 05 and represents the top of the type-safety chain. After this ticket, the entire call path from `Register.matches()` through `factory()`, `Repository.matches()`, `Line.read()`, `Field.read()` down to `_textual_read()` / `_binary_read()` has precise type annotations, enabling mypy to catch type mismatches at every layer.

### Current State

**`cfinterface/components/register.py`**:

- `Register.matches(cls, line: Union[str, bytes], storage: Union[str, StorageType] = "")` -- calls `factory(storage).matches(cls.IDENTIFIER, line[:cls.IDENTIFIER_DIGITS])`
- `Register.read(self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs) -> bool` -- creates a new `Line(fields, delimiter, storage=storage)` on each call, reads from `factory(storage).read(file, linesize)`, delegates to `line.read()`
- `Register.write(self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs) -> bool` -- creates a new `Line`, delegates to `line.write()`, then `factory(storage).write(file, linedata)`
- `Register.read_register()` and `write_register()` are convenience wrappers

**`cfinterface/components/block.py`**:

- `Block.begins(cls, line: Union[str, bytes], storage: Union[str, StorageType] = "")` -- calls `factory(storage).begins(cls.BEGIN_PATTERN, line)`
- `Block.ends(cls, line: Union[str, bytes], storage: Union[str, StorageType] = "")` -- calls `factory(storage).ends(cls.END_PATTERN, line)`
- `Block.read(self, file: IO, *args, **kwargs) -> bool` -- raises `NotImplementedError` (consumers implement this)
- `Block.write(self, file: IO, *args, **kwargs) -> bool` -- raises `NotImplementedError`

**`cfinterface/components/section.py`**:

- `Section.read(self, file: IO, *args, **kwargs) -> bool` -- raises `NotImplementedError`
- `Section.write(self, file: IO, *args, **kwargs) -> bool` -- raises `NotImplementedError`
- Has `STORAGE` class attribute but no `storage` method parameter

**`cfinterface/components/defaultregister.py`**:

- `DefaultRegister.read(self, file: IO, storage: Union[str, StorageType] = "", ...)` -- checks `storage != StorageType.BINARY`
- `DefaultRegister.write(self, file: IO, storage: Union[str, StorageType] = "", ...)` -- checks `storage != StorageType.BINARY`

**`cfinterface/components/defaultblock.py`** and **`cfinterface/components/defaultsection.py`**:

- Simple implementations that read/write via `file.readline()` and `file.write()`. No `storage` parameter.

## Specification

### Requirements

1. **Add `@overload` to `Register.matches()`**:
   - `matches(cls, line: str, storage: Union[str, StorageType] = "") -> bool`
   - `matches(cls, line: bytes, storage: Union[str, StorageType] = "") -> bool`
     The overloads differentiate the `line` parameter type. The `storage` parameter stays `Union[str, StorageType]` because it can be a plain string, the `StorageType` enum, or the empty-string sentinel.

2. **Add `@overload` to `Block.begins()` and `Block.ends()`**:
   - Same pattern as `Register.matches()` -- overload on the `line` parameter type.

3. **Tighten `Register.read()` and `Register.write()` type annotations**:
   - Keep `storage: Union[str, StorageType] = ""` as the parameter type (cannot be narrowed due to the 254+ downstream subclasses that pass plain strings).
   - Add explicit `IO` type narrowing in the docstring: "When `storage` is `StorageType.BINARY`, `file` should be a `BinaryIO`; when textual, `file` should be a `TextIO`."
   - Do NOT add `@overload` to `read()`/`write()` based on the `storage` parameter -- this would be fragile because the overloads would differ only in the `storage` default value, and callers rarely pass `storage` as a keyword argument directly (it is threaded from the reading/writing layer via `*args, **kwargs`).

4. **Tighten `DefaultRegister.read()` and `DefaultRegister.write()`**:
   - Keep the `storage != StorageType.BINARY` runtime check -- this is correct and necessary.
   - Narrow the type annotation of `storage` to `Union[str, StorageType]` (already correct; no change needed).

5. **Do NOT modify `Block.read()`/`Block.write()` or `Section.read()`/`Section.write()`**:
   - These raise `NotImplementedError` on the base class and are fully implemented by consumer subclasses via `*args, **kwargs`. Adding overloads here would break the subclass contract since consumers define their own `read()` signatures with different parameters.

6. **Do NOT modify `DefaultBlock` or `DefaultSection`**:
   - These do not use a `storage` parameter and have simple `file.readline()`/`file.write()` implementations. No type narrowing is needed.

7. **Add type narrowing comments** in `Register.read()` and `Register.write()` where `factory(storage).read()` and `factory(storage).write()` are called, so that mypy understands the flow better. Use `# type: ignore[arg-type]` sparingly if needed for the `factory()` polymorphic return.

### Inputs/Props

- No changes to runtime inputs. Only type annotations and overloads are added.

### Outputs/Behavior

- Runtime behavior is identical.
- mypy can verify that `Register.matches("text", "line")` and `Register.matches(b"text", b"line")` are both valid.
- mypy can verify that `Block.begins("text", "line")` is valid but `Block.begins(123, "line")` is not.

### Error Handling

- No changes to error handling.

## Acceptance Criteria

- [ ] Given `cfinterface/components/register.py`, when inspected, then `Register.matches()` has `@overload` signatures for `str` and `bytes` line parameters.
- [ ] Given `cfinterface/components/block.py`, when inspected, then `Block.begins()` and `Block.ends()` have `@overload` signatures for `str` and `bytes` line parameters.
- [ ] Given `cfinterface/components/register.py`, when inspected, then `Register.read()` and `Register.write()` have updated docstrings noting the `file` type contract.
- [ ] Given `Block.read()` and `Block.write()`, when inspected, then they are NOT modified (still raise `NotImplementedError`).
- [ ] Given `Section.read()` and `Section.write()`, when inspected, then they are NOT modified.
- [ ] Given `DefaultRegister`, `DefaultBlock`, `DefaultSection`, when inspected, then `DefaultRegister` retains its `storage != StorageType.BINARY` check and `DefaultBlock`/`DefaultSection` are unchanged.
- [ ] Given `pytest tests/`, when run, then all 268+ tests pass.
- [ ] Given `ruff check cfinterface/components/`, when run, then no lint errors are reported.
- [ ] Given `mypy --strict cfinterface/components/register.py cfinterface/components/block.py`, when run, then no errors related to the overloaded methods are reported (other pre-existing mypy issues may exist).

## Implementation Guide

### Suggested Approach

**Step 1: Add overloads to `Register.matches()`**

```python
from typing import Any, IO, Union, List, overload
from cfinterface.storage import StorageType

class Register:
    # ... existing code ...

    @classmethod
    @overload
    def matches(
        cls, line: str, storage: Union[str, StorageType] = ""
    ) -> bool: ...

    @classmethod
    @overload
    def matches(
        cls, line: bytes, storage: Union[str, StorageType] = ""
    ) -> bool: ...

    @classmethod
    def matches(
        cls, line: Union[str, bytes], storage: Union[str, StorageType] = ""
    ):
        return factory(storage).matches(
            cls.IDENTIFIER, line[: cls.IDENTIFIER_DIGITS]
        )
```

Note: `@classmethod` must come before `@overload` in the decorator stack for the overload declarations. For the implementation method, `@classmethod` is the only decorator.

**Step 2: Add overloads to `Block.begins()` and `Block.ends()`**

Follow the same pattern as `Register.matches()`:

```python
@classmethod
@overload
def begins(
    cls, line: str, storage: Union[str, StorageType] = ""
) -> bool: ...

@classmethod
@overload
def begins(
    cls, line: bytes, storage: Union[str, StorageType] = ""
) -> bool: ...

@classmethod
def begins(
    cls, line: Union[str, bytes], storage: Union[str, StorageType] = ""
):
    return factory(storage).begins(cls.BEGIN_PATTERN, line)
```

Same pattern for `ends()`.

**Step 3: Update `Register.read()` and `Register.write()` docstrings**

Add a note about the expected `file` type:

```python
def read(
    self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs
) -> bool:
    """
    Reads the register from the file.

    :param file: The file pointer. Should be TextIO when storage
        is TEXT (default), or BinaryIO when storage is BINARY.
    :type file: IO
    :param storage: The storage type (TEXT or BINARY)
    :type storage: str | StorageType
    :return: True when reading succeeds
    :rtype: bool
    """
```

**Step 4: Add `overload` import to both files**

Ensure `overload` is imported from `typing` in both `register.py` and `block.py`.

**Step 5: Verify and run tests**

```bash
pytest tests/
ruff check cfinterface/components/register.py cfinterface/components/block.py
```

### Key Files to Modify

- `cfinterface/components/register.py` -- add overloads to `matches()`, update `read()`/`write()` docstrings
- `cfinterface/components/block.py` -- add overloads to `begins()` and `ends()`

### Files NOT Modified

- `cfinterface/components/section.py` -- no `storage`-parameterized methods to overload
- `cfinterface/components/defaultregister.py` -- runtime check is correct, no type changes needed
- `cfinterface/components/defaultblock.py` -- no `storage` parameter
- `cfinterface/components/defaultsection.py` -- no `storage` parameter

### Patterns to Follow

- Follow the `@overload` pattern from tickets 017-018.
- Use `@classmethod` before `@overload` in decorator order.
- Keep implementation signatures with `Union[str, bytes]`.

### Pitfalls to Avoid

- Do NOT add `@overload` to `Register.read()`/`Register.write()` based on the `storage` parameter -- mypy cannot narrow based on a default-valued parameter that is sometimes omitted by callers. The overload would not provide real value and would add maintenance burden.
- Do NOT modify `Block.read()` or `Block.write()` -- these are `NotImplementedError` stubs meant to be overridden by consumer subclasses. Adding overloads would impose a contract on consumer implementations.
- Do NOT change the `*args, **kwargs` passthrough on `Register.read()`, `Register.write()`, `Block.read()`, `Block.write()`, `Section.read()`, `Section.write()` -- these are load-bearing and allow consumer subclasses to accept custom parameters.
- Do NOT remove the `storage` parameter from any method -- it is threaded from the reading/writing layer and 254+ downstream subclasses depend on this interface.
- Be aware that `@classmethod` + `@overload` ordering matters. In the overload declarations, use `@classmethod` then `@overload`. In the implementation, use only `@classmethod`.

## Testing Requirements

### Unit Tests

- Append to `tests/components/test_register.py`:
  - Test that `DummyRegister.matches("reg test", "")` returns `True` with default storage.
  - Test that `DummyRegister.matches("reg test", StorageType.TEXT)` returns `True`.
  - Test that `DummyBinaryRegister.matches(b"...", StorageType.BINARY)` works for binary.

- Append to `tests/components/test_block.py`:
  - Test that a dummy block's `begins()` class method works with `str` and `bytes` arguments.
  - Test that `ends()` class method works with `str` and `bytes` arguments.

### Integration Tests

- Run the full test suite (`pytest tests/`) to confirm no regressions.
- Specifically verify the register read/write tests still pass: `pytest tests/components/test_register.py tests/components/test_defaultregister.py`.

### E2E Tests (if applicable)

- Not applicable.

## Dependencies

- **Blocked By**: ticket-019
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
