# ticket-011 Create conftest.py with Shared Test Fixtures

## Context

### Background

The cfinterface test suite currently has 392+ tests across 20+ test files but lacks a `conftest.py` at any level. Test setup code for creating field instances, parser configurations, and mock file objects is duplicated across multiple test files. For example, `tests/components/test_tabular.py` defines helper functions like `_make_integer_parser()` and `_make_mixed_parser()`, `tests/components/test_floatfield.py` manually constructs FloatField instances in every test function, and the `tests/mocks/mock_open.py` module provides a custom mock for seek/tell support that must be explicitly imported.

Epics 1 and 2 have been completed: `pyproject.toml` now has `[tool.pytest.ini_options]` with `--strict-markers`, markers `slow` and `benchmark` are registered, and `hypothesis` plus `pytest-benchmark` are installed as dev dependencies.

### Relation to Epic

This is the first ticket in Epic 03 (Test Infrastructure Enhancement). It establishes the shared fixture infrastructure that ticket-012 (hypothesis field tests) and ticket-013 (hypothesis tabular tests) depend on for reusable hypothesis strategies and field factory fixtures.

### Current State

- No `conftest.py` exists anywhere under `tests/`.
- `tests/mocks/mock_open.py` provides a custom `mock_open` function supporting seek/tell -- it is imported manually in test files that need it.
- `tests/components/test_tabular.py` defines local helper functions `_make_integer_parser()`, `_make_mixed_parser()`, `_make_semicolon_parser()`, `_make_comma_float_parser()`, and `_build_file()`.
- Each field test file (`test_floatfield.py`, `test_integerfield.py`, etc.) constructs fields inline with no reuse.
- The `Field` base class (in `cfinterface/components/field.py`) uses `__slots__` with `_size`, `_starting_position`, `_ending_position`, `_value`.
- Field constructors follow the pattern `FieldType(size, starting_position, ..., value=None)`.

## Specification

### Requirements

1. Create `tests/conftest.py` at the test root level with:
   - A `mock_open_seekable` fixture that wraps the existing `tests/mocks/mock_open.py` function and returns a factory callable (function scope).
   - A `tmp_text_file` fixture that creates a `pytest.tmp_path`-based temporary text file factory (function scope).
   - A `tmp_binary_file` fixture that creates a `pytest.tmp_path`-based temporary binary file factory (function scope).

2. Create `tests/components/conftest.py` with:
   - Factory fixtures for field instances: `integer_field_factory`, `float_field_factory`, `literal_field_factory`, `datetime_field_factory`. Each returns a callable that accepts keyword overrides for the constructor parameters and returns a fresh field instance.
   - `tabular_parser_factory` fixture that returns a callable accepting a list of `ColumnDef` and optional `delimiter` and returns a `TabularParser`.
   - `make_string_io` fixture that returns a callable accepting a list of lines and returning an `io.StringIO` (replacing `_build_file()` patterns).

3. All fixtures must use function scope (default) to avoid cross-test contamination since fields use `__slots__` and are mutable.

4. Existing tests must NOT be modified. New fixtures are for use by new tests in tickets 012, 013, 014.

### Inputs/Props

- No external inputs. Fixtures are self-contained factory functions.

### Outputs/Behavior

- `tests/conftest.py` -- shared fixtures available to all tests.
- `tests/components/conftest.py` -- component-specific fixtures available to `tests/components/` tests.

### Error Handling

- Field factory fixtures must not catch exceptions; if invalid parameters are passed, the underlying constructor's error should propagate naturally.

## Acceptance Criteria

- [ ] Given the file `tests/conftest.py` does not exist, when ticket-011 is implemented, then the file `tests/conftest.py` exists and is valid Python (importable without error).
- [ ] Given the file `tests/components/conftest.py` does not exist, when ticket-011 is implemented, then the file `tests/components/conftest.py` exists and is valid Python (importable without error).
- [ ] Given `tests/conftest.py` is loaded by pytest, when a test function declares a parameter named `mock_open_seekable`, then the fixture provides a callable that returns a MagicMock object with working `seek()` and `tell()` methods.
- [ ] Given `tests/components/conftest.py` is loaded by pytest, when a test function declares `integer_field_factory`, then calling `integer_field_factory(size=4, starting_position=0, value=42)` returns an `IntegerField` instance with `value == 42`.
- [ ] Given `tests/components/conftest.py` is loaded by pytest, when a test function declares `float_field_factory`, then calling `float_field_factory(size=8, starting_position=0, decimal_digits=2, format="F", value=1.23)` returns a `FloatField` instance with `value == 1.23`.
- [ ] Given the full test suite is executed with `pytest tests/`, when all 392+ existing tests run, then all pass with zero new failures (exit code 0).
- [ ] Given `ruff check tests/conftest.py tests/components/conftest.py` is executed, then zero violations are reported.

## Implementation Guide

### Suggested Approach

1. Create `tests/conftest.py` with root-level fixtures:

   ```python
   import pytest
   from tests.mocks.mock_open import mock_open

   @pytest.fixture()
   def mock_open_seekable():
       """Factory fixture: returns mock_open(read_data=data) with seek/tell support."""
       def _factory(read_data=""):
           return mock_open(read_data=read_data)
       return _factory

   @pytest.fixture()
   def tmp_text_file(tmp_path):
       """Factory: create a temp text file with given content, return its Path."""
       def _factory(content: str, name: str = "test.txt"):
           p = tmp_path / name
           p.write_text(content)
           return p
       return _factory

   @pytest.fixture()
   def tmp_binary_file(tmp_path):
       """Factory: create a temp binary file with given content, return its Path."""
       def _factory(content: bytes, name: str = "test.bin"):
           p = tmp_path / name
           p.write_bytes(content)
           return p
       return _factory
   ```

2. Create `tests/components/conftest.py` with component-specific fixtures:

   ```python
   import io
   import pytest
   from cfinterface.components.integerfield import IntegerField
   from cfinterface.components.floatfield import FloatField
   from cfinterface.components.literalfield import LiteralField
   from cfinterface.components.datetimefield import DatetimeField
   from cfinterface.components.tabular import TabularParser

   @pytest.fixture()
   def integer_field_factory():
       def _factory(size=8, starting_position=0, value=None):
           return IntegerField(size, starting_position, value=value)
       return _factory

   @pytest.fixture()
   def float_field_factory():
       def _factory(size=8, starting_position=0, decimal_digits=4, format="F", sep=".", value=None):
           return FloatField(size, starting_position, decimal_digits, format=format, sep=sep, value=value)
       return _factory

   @pytest.fixture()
   def literal_field_factory():
       def _factory(size=80, starting_position=0, value=None):
           return LiteralField(size, starting_position, value=value)
       return _factory

   @pytest.fixture()
   def datetime_field_factory():
       def _factory(size=16, starting_position=0, format="%Y/%m/%d", value=None):
           return DatetimeField(size, starting_position, format=format, value=value)
       return _factory

   @pytest.fixture()
   def tabular_parser_factory():
       def _factory(columns, delimiter=None):
           return TabularParser(columns, delimiter=delimiter)
       return _factory

   @pytest.fixture()
   def make_string_io():
       def _factory(lines):
           return io.StringIO("".join(lines))
       return _factory
   ```

3. Run `pytest tests/` to confirm all existing tests still pass.
4. Run `ruff check tests/conftest.py tests/components/conftest.py`.

### Key Files to Modify

- `tests/conftest.py` (CREATE)
- `tests/components/conftest.py` (CREATE)

### Patterns to Follow

- Use the factory fixture pattern (`fixture returns a callable`) to allow parametrized instantiation in each test. This is the standard pytest idiom for reusable object construction.
- Default parameter values in factories match the constructor defaults of each field class.
- Do NOT use `autouse=True` on any fixture.

### Pitfalls to Avoid

- Do NOT modify any existing test files. Existing tests must remain untouched to avoid regression risk.
- Do NOT use session or module scope for fixtures that return mutable objects (fields mutate `_value` in-place via `read()`).
- Do NOT import `pandas` at module level in conftest; it is an optional dependency and would break test collection on environments without it.
- Do NOT create a `conftest.py` that shadows the existing `tests/mocks/mock_open.py` -- the fixture wraps it, not replaces it.

## Testing Requirements

### Unit Tests

No dedicated unit tests for conftest.py itself. Fixture correctness is validated by:

1. The existing 392+ tests continue to pass (no interference).
2. The acceptance criteria above, which can be verified manually or by writing a small smoke test (optional).

### Integration Tests

Not applicable -- fixtures are verified through downstream usage in tickets 012-014.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-002-add-pytest-configuration.md (markers and config must be in place), ticket-006-add-py-typed-and-dev-deps.md (hypothesis/pytest-benchmark installed)
- **Blocks**: ticket-012-add-hypothesis-field-tests.md, ticket-013-add-hypothesis-tabular-tests.md

## Effort Estimate

**Points**: 1
**Confidence**: High
