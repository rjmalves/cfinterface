# Epic 05 Learnings — Type-Safe Text/Binary Dispatch

**As of**: 2026-02-23
**Tickets**: 017, 018, 019, 020
**Test count after epic**: 292 (268 at start + 24 new)

---

## Patterns Established

### `@overload` + `_T` TypeVar for str/bytes polymorphism

- Module-level `_T = TypeVar("_T", str, bytes)` in `cfinterface/components/field.py` enables
  the `write(self, line: _T) -> _T` implementation signature while `@overload` stubs give
  callers precise narrowed types (`str -> str`, `bytes -> bytes`).
- The implementation signature keeps `_T` so mypy can verify the body is type-correct internally;
  removing it from the implementation would cause mypy to widen the return to `str | bytes`.
- The old class-level `Field.T = TypeVar(...)` was non-standard and has been removed entirely;
  it was never part of the public API and no downstream code referenced it.

### `@classmethod` + `@overload` decorator ordering

- For class methods with overloads, `@classmethod` MUST come before `@overload` in each stub,
  but the implementation method carries only `@classmethod` (not both).
- See `cfinterface/components/register.py` (`matches`) and `cfinterface/components/block.py`
  (`begins`, `ends`) as canonical references for this ordering.

### Three-overload `factory()` pattern

- All four `factory()` functions now use three overloads:
  `Literal["TEXT"] -> Type[TextualRepository]`,
  `Literal["BINARY"] -> Type[BinaryRepository]`,
  `Union[str, StorageType] -> Type[Repository]` (fallback for runtime values).
- The third (fallback) overload is required so that call sites that hold a runtime
  `Union[str, StorageType]` variable still type-check without error.
- All four modules follow this identical pattern:
  `cfinterface/adapters/components/repository.py`,
  `cfinterface/adapters/components/line/repository.py`,
  `cfinterface/adapters/reading/repository.py`,
  `cfinterface/adapters/writing/repository.py`.

### Abstract base keeps `Union`, concrete subclasses narrow

- The abstract `Repository` base class in every adapter module retains `Union[str, bytes]` for
  all method signatures; only `TextualRepository` and `BinaryRepository` use `str` or `bytes`
  specifically.
- This is load-bearing: callers that hold a `Repository` reference from `factory()` at runtime
  (before mypy can resolve the overload) need the broad base type.
- `cfinterface/adapters/components/line/repository.py` demonstrates both sides: the
  `TextualRepository.read(line: str, delimiter: Optional[str])` concrete signature is narrow,
  while `Repository.read(line: Any, delimiter: Optional[Union[str, bytes]])` stays broad.

### `write()` body simplification (single isinstance branch)

- `Field.write()` was refactored from two nested `isinstance` checks to a single
  `isinstance(line, bytes)` branch that produces the value and assembles the line in one pass.
- The unreachable `else: return line` fallback was removed.
- The `line = line.ljust(self.ending_position)` reassignment (both `str` and `bytes`) is kept
  inside both branches and is idiomatic -- immutable objects reassigned in local scope.

---

## Architectural Decisions

### Decision: `Line.write()` return type stays `Union[str, bytes]`

- **Rejected**: adding `@overload` to `Line.write()` based on a storage-mode discriminator.
- **Rationale**: `write()` takes only `values: List[Any]` -- there is no typed argument to
  discriminate on. The storage mode is a runtime value from `__init__`, not visible to the
  type checker at call sites. A discriminator-less overload would provide no narrowing benefit
  and would require every caller to carry a `cast()` or `# type: ignore`.
- The return type remains `Union[str, bytes]` in `cfinterface/components/line.py`.

### Decision: `Line` is NOT made generic (`Line[str]` / `Line[bytes]`)

- **Rejected**: parameterizing `Line` over the storage type as `Generic[_T]`.
- **Rationale**: 254+ downstream consumer subclasses set class-level `LINE = Line(fields)`
  without a type argument. Making `Line` generic would be a breaking change for every
  downstream file format implementation. The marginal type-checking benefit does not justify
  the migration cost.

### Decision: abstract `Repository` base retains broad signatures

- **Rejected**: narrowing the abstract base to use overloads.
- **Rationale**: `RegisterReading`, `BlockReading`, etc. hold a `Repository` base reference and
  call methods polymorphically. Narrowing the base would force all call sites to downcast.

### Decision: `BinaryRepository.matches()` special case NOT overloaded

- The implementation in `cfinterface/adapters/components/repository.py` handles both
  `(bytes, bytes)` and `(str, bytes)` at runtime using `isinstance(pattern, bytes)`.
- The ticket specification called for `@overload` on `BinaryRepository.matches()`, but the
  implementation chose to keep a single `Union[str, bytes]` signature on the concrete method
  (which satisfies the abstract base). The overloads were applied only to `factory()`, not to
  the instance methods of the concrete `BinaryRepository`.

### Decision: `isinstance` guards kept in writing repository

- `cfinterface/adapters/writing/repository.py` `TextualRepository.write()` and
  `BinaryRepository.write()` retain their `isinstance(data, ...)` runtime guards for backward
  compatibility, even though the type signatures now narrow the parameter type.
- This avoids silent data corruption if a caller passes the wrong type through a `# type: ignore`.

---

## Files and Structures Created / Modified

- `cfinterface/components/field.py` -- module-level `_T`, `@overload` on `read()` and `write()`,
  simplified single-branch `write()` body; `Field.T` class attribute removed.
- `cfinterface/components/line.py` -- `@overload` on `read()` only; `write()` stays
  `Union[str, bytes]`; `overload` added to imports.
- `cfinterface/components/register.py` -- `@overload` on `matches()` for `str` and `bytes` line;
  `overload` added to imports.
- `cfinterface/components/block.py` -- `@overload` on `begins()` and `ends()` for `str` and `bytes`
  line; `overload` added to imports.
- `cfinterface/adapters/components/repository.py` -- three-overload `factory()`;
  `TextualRepository` methods narrowed to `str`; `BinaryRepository` methods narrowed to `bytes`;
  `Literal` imported from `typing`.
- `cfinterface/adapters/components/line/repository.py` -- three-overload `factory()`;
  `TextualRepository.read/write` narrowed to `str`; `BinaryRepository.read/write` narrowed to
  `bytes`; delimiter types matched to line types.
- `cfinterface/adapters/reading/repository.py` -- three-overload `factory()`; `BinaryIO`/`TextIO`
  used for `_filepointer` type; `BinaryRepository.read` returns `bytes`, `TextualRepository.read`
  returns `str`.
- `cfinterface/adapters/writing/repository.py` -- three-overload `factory()`; `BinaryRepository`
  narrowed to `bytes`, `TextualRepository` narrowed to `str`.
- `tests/components/test_field.py` -- appended tests for `_T` at module level, `write()` str/bytes
  return types, no `Field.T` attribute.
- `tests/adapters/components/test_linerepository.py` -- appended tests for binary read/write,
  `BinaryRepository.write()` returns `bytes`.
- `tests/adapters/components/test_registerrepository.py` -- appended tests for
  `BinaryRepository.matches()` with `str` pattern + `bytes` line, and `bytes` pattern + `bytes`
  line.
- `tests/components/test_register.py` -- appended tests for `matches()` with `StorageType.TEXT`
  and `StorageType.BINARY`.
- `tests/components/test_block.py` -- appended tests for `begins()` and `ends()` with `str` and
  `bytes` arguments.

---

## Conventions Adopted

- **`_T` at module level, not class level**: TypeVars used in `@overload` stacks must be
  module-level. A class-level TypeVar breaks the overload mechanism. See `field.py`.
- **Overload stubs are minimal (ellipsis body)**: Each `@overload` stub ends with `...` only --
  no docstring, no logic. The docstring lives on the implementation method.
- **`Literal["TEXT"]` and `Literal["BINARY"]` in factory overloads**: Because `StorageType(str, Enum)`
  means `StorageType.TEXT == "TEXT"`, a `Literal["TEXT"]` overload covers both the enum member
  and the plain string. No separate `StorageType.TEXT` overload is needed.
- **Abstract base class docstring placement**: Not changed -- docstrings stay on abstract methods
  only; concrete implementations inherit them silently.
- **`# type: ignore` retained in `line/repository.py`**: The `field.read(line)` call in
  `BinaryRepository.read()` retains its `# type: ignore` comment because mypy still cannot
  prove the `line: bytes` narrows through `Field.read()` in that context.

---

## Surprises and Deviations

### `BinaryRepository.matches()` overload not applied

- **Planned**: ticket-018 specified adding `@overload` to `BinaryRepository.matches()` for
  `(bytes, bytes)` and `(str, bytes)`.
- **Actual**: The implementation kept a single `Union[str, bytes]` parameter type on the concrete
  method. The overloads were applied to `factory()` instead, which delivers more value (call-site
  narrowing from `factory()` return type) at lower risk.
- **Where**: `cfinterface/adapters/components/repository.py` lines 47-51.

### `Line.write()` cannot be overloaded -- confirmed

- **Planned**: ticket-019 considered but rejected overloading `write()`.
- **Actual**: Confirmed in implementation. The return type is fundamentally determined by the
  storage mode (a constructor argument), not by any argument to `write()`. No overload is
  possible without making `Line` generic.
- **Where**: `cfinterface/components/line.py` line 52.

### Test count grew by 24, not the ~10 estimated

- New tests added across 5 test files (field, register, block, linerepository,
  registerrepository), reaching 292 total. The binary path tests (which had sparse coverage
  before) contributed more cases than anticipated.

---

## Recommendations for Future Epics

### For epic-06 (generic tabular parser)

- The `Line` class cannot be made generic without breaking 254+ subclasses; the tabular parser
  should follow the same pattern: a concrete class with a `storage: Union[str, StorageType]`
  constructor argument, not a generic class.
- Use the `@overload` + three-overload `factory()` pattern (established in all four adapter
  modules) for any new parser-level `factory()` function.
- The `TextualRepository` in `cfinterface/adapters/components/line/repository.py` is the
  reference for delimiter-based positional reading -- the tabular engine should extend or
  compose this, not duplicate it.
- The `_compile()` / `_pattern_cache` from `cfinterface/adapters/components/repository.py`
  is available for reuse in any new pattern-matching logic.

### For epic-07 (schema versioning and batch ops)

- The `storage: Union[str, StorageType]` parameter threading convention (Register.read/write,
  Block.begins/ends) is load-bearing and must not be narrowed. Schema version dispatch should
  follow the same thread-from-the-top pattern.
- Any new `factory()` function for schema versions should apply the same three-overload structure
  established in this epic.
- The `Literal["TEXT"]` / `Literal["BINARY"]` overload approach works because the values are
  known statically; schema version literals (e.g., `Literal["v1"]`, `Literal["v2"]`) would
  work with the same technique.
