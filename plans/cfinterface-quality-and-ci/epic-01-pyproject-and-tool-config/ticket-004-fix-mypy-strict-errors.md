# ticket-004 Fix mypy Strict Type Annotation Errors

## Context

### Background

After ticket-003 adds the mypy configuration with `disallow_untyped_defs`, `warn_return_any`, and `strict_optional`, a temporary `ignore_errors = true` override suppresses 189 errors across 29 files. This ticket systematically fixes those errors by adding type annotations and resolving type incompatibilities, then removes the temporary override so mypy runs cleanly with strict flags.

### Relation to Epic

Fourth ticket in Epic 1. This is the largest ticket in the epic and the most technically involved. It transforms the codebase from permissively typed to strictly typed under the three target flags.

### Current State

Running `uv run mypy --disallow-untyped-defs --warn-return-any --strict-optional ./cfinterface` produces 189 errors:

- 137 `no-untyped-def` (missing return type or parameter annotations)
- 22 `no-any-return` (returning `Any` from typed function)
- 14 `override` (incompatible method signatures in subclasses)
- 6 `arg-type` (incompatible argument types)
- 3 `misc` (incompatible yield types)
- 3 `assignment` (incompatible assignment types)
- 2 `import-untyped` (pandas stubs, handled by override)
- 2 `unused-ignore` (integerfield.py and floatfield.py have stale `# type: ignore` comments)

Files grouped by subsystem:

- **components/** (14 files, ~80 errors): section.py, block.py, register.py, line.py, field.py, floatfield.py, integerfield.py, literalfield.py, datetimefield.py, defaultregister.py, defaultblock.py, defaultsection.py, tabular.py
- **data/** (3 files, ~41 errors): registerdata.py, blockdata.py, sectiondata.py
- **files/** (3 files, ~23 errors): registerfile.py, blockfile.py, sectionfile.py
- **reading/** (3 files, ~9 errors): registerreading.py, blockreading.py, sectionreading.py
- **writing/** (3 files, ~9 errors): registerwriting.py, blockwriting.py, sectionwriting.py
- **adapters/** (4 files, ~41 errors): components/repository.py, components/line/repository.py, reading/repository.py, writing/repository.py
- **versioning.py** (1 error)

## Specification

### Requirements

1. Add type annotations to all function signatures in the 29 affected files so that `no-untyped-def` errors are resolved
2. Fix `no-any-return` errors by adding appropriate type casts or refining return type annotations
3. Fix `override` errors in adapter repositories by adjusting method signatures to be compatible with base class (use `Union[str, bytes]` parameter types where the base class expects them, or use `@overload` where needed)
4. Fix `arg-type` and `assignment` errors in data containers (registerdata.py, blockdata.py, sectiondata.py) by refining generic type usage
5. Fix `misc` errors (yield type mismatches) in data containers by adjusting generic bounds
6. Remove stale `# type: ignore` comments in integerfield.py (line 2) and floatfield.py (line 2) that produce `unused-ignore` warnings
7. Remove the temporary `ignore_errors = true` override block from pyproject.toml (added by ticket-003)

### Inputs/Props

- All 29 Python files listed in Current State
- `/home/rogerio/git/cfinterface/pyproject.toml` (to remove temporary override)

### Outputs/Behavior

- `uv run mypy ./cfinterface` exits with return code 0 and reports "Success: no issues found"
- All 392 existing tests still pass
- No behavioral changes to any function

### Error Handling

- Type annotations must be accurate — do NOT use `Any` to silence errors unless the existing behavior genuinely operates on `Any`
- Do NOT change function behavior, only add/refine type annotations
- For `data` parameter in constructors (section.py, block.py, register.py), use `Optional[Any]` since these accept diverse types
- For IO parameters, use `IO[str]` or `IO[bytes]` as appropriate based on StorageType

## Acceptance Criteria

- [ ] Given the updated codebase, when running `uv run mypy ./cfinterface`, then mypy reports "Success: no issues found" with return code 0
- [ ] Given the updated pyproject.toml, when searching for `ignore_errors = true`, then no such line exists (the temporary override has been removed)
- [ ] Given the updated codebase, when running `uv run pytest -q`, then all 392 tests pass
- [ ] Given the files `cfinterface/components/integerfield.py` and `cfinterface/components/floatfield.py`, when inspecting line 2, then no stale `# type: ignore` comment exists

## Implementation Guide

### Suggested Approach

Work through files in dependency order (bottom-up):

1. **versioning.py** (1 error) — Add parameter annotation to `validate_version.data`
2. **components/field.py, floatfield.py, integerfield.py, literalfield.py, datetimefield.py** (~5 errors) — Add return types to `_textual_write`, `_textual_read`, etc. Remove stale `# type: ignore` on line 2 of integerfield.py and floatfield.py
3. **components/line.py** (~9 errors) — Add annotations to read/write methods
4. **components/section.py, block.py, register.py** (~37 errors) — Add annotations to `__init__`, read, write, `__eq__`, property methods. For `data` parameter use `Optional[Any]`. For `previous`/`next` parameters use `Optional[Any]`
5. **components/defaultregister.py, defaultblock.py, defaultsection.py** (~10 errors) — Add annotations matching parent class signatures
6. **components/tabular.py** (~5 errors) — Fix `str | bytes` append issue by using `cast` or conditional logic
7. **data/registerdata.py, blockdata.py, sectiondata.py** (~41 errors) — Add return types to all dunder methods. Fix generic `T` yield/arg issues by adjusting `TypeVar` bound or using `cast`
8. **files/registerfile.py, blockfile.py, sectionfile.py** (~23 errors) — Add annotations to `__init__`, `read`, `write`, `read_many`, `validate`. Fix `no-any-return` with explicit return types
9. **reading/registerreading.py, blockreading.py, sectionreading.py** (~9 errors) — Add annotations to private helper methods
10. **writing/registerwriting.py, blockwriting.py, sectionwriting.py** (~9 errors) — Add annotations to private write methods
11. **adapters/** (~41 errors) — Fix `override` errors by making method signatures compatible with base Repository. Use `Union[str, bytes]` for parameters where the base expects it, or add `@overload` decorators

After all files are fixed: 12. Remove the `ignore_errors = true` override block from pyproject.toml 13. Run `uv run mypy ./cfinterface` to confirm 0 errors 14. Run `uv run pytest -q` to confirm all 392 tests pass

### Key Files to Modify

All 29 files listed in Current State, plus:

- `/home/rogerio/git/cfinterface/pyproject.toml` (remove temporary override)

### Patterns to Follow

- Use `from __future__ import annotations` at the top of files if needed to avoid circular imports in type annotations
- Use `Optional[X]` for parameters with `None` defaults
- Use `IO[str]` / `IO[bytes]` for file handle parameters (import from `typing`)
- Use `Union[str, bytes]` where a method handles both text and binary
- For `data` parameters in component constructors, use `Optional[Any]` to match existing permissive behavior
- Follow the existing type annotation style already present in `storage.py` and `versioning.py`

### Pitfalls to Avoid

- Do NOT change any function's runtime behavior — annotation-only changes
- Do NOT use `# type: ignore` to suppress new errors — fix them properly
- Do NOT add `Any` annotations where a more specific type is possible
- Do NOT change function signatures in ways that would break existing callers
- Be careful with the `override` errors in adapters — the base Repository class defines `read(content: Union[str, bytes])` and `write(content: Union[str, bytes])`, but subclasses narrow to `str` or `bytes`. Use `Union[str, bytes]` in the subclass parameter and handle dispatch internally, or add `@overload` pairs
- The `data` container `T` TypeVar issues (`yield`, `remove` arg-type) need careful handling — the TypeVar may need an upper bound adjustment

## Testing Requirements

### Unit Tests

- Run the full test suite: `uv run pytest -q` — all 392 tests must pass
- No new tests needed (this is annotation-only)

### Integration Tests

- Run `uv run mypy ./cfinterface` — must report 0 errors
- Run `uv run ruff check ./cfinterface` — must still pass (no ruff regressions)

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-003-add-mypy-configuration (must have the mypy config with temporary overrides in place)
- **Blocks**: ticket-008-extract-lint-job (CI lint job runs mypy without ignores)

## Effort Estimate

**Points**: 5
**Confidence**: Medium (189 errors across 29 files; most are mechanical annotation additions, but adapter override issues and data container generics may require design decisions)
