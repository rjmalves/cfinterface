# ticket-012 Add Hypothesis Property-Based Tests for Field Round-Trips

## Context

### Background

The cfinterface field classes (FloatField, IntegerField, LiteralField, DatetimeField) all implement textual `read(str)` / `write(str)` and binary `read(bytes)` / `write(bytes)` operations. The fundamental correctness property is: for a valid value, `write()` followed by `read()` should recover the original value (within type-appropriate tolerance for floats). Currently, `test_floatfield.py` has a hand-rolled fuzz test (`test_floatfield_write_fuzz_equivalence`) using `random.seed(42)` with 50,000 iterations, but no other field type has property-based coverage. The hypothesis library is already installed as a dev dependency (from Epic 01).

### Relation to Epic

This is the second ticket in Epic 03. It introduces hypothesis property-based testing for field-level round-trips, building on the conftest fixtures established in ticket-011. It validates correctness across a wide input domain rather than relying on manually chosen examples.

### Current State

- `hypothesis` is listed in `[project.optional-dependencies] dev` in `pyproject.toml`.
- `tests/components/test_floatfield.py` has `test_floatfield_write_fuzz_equivalence()` (lines 180-198) that uses `random.seed(42)` and tests 50,000 random inputs against a reference implementation. This test takes significant time but is not marked `slow`.
- `tests/components/test_integerfield.py` has 10 tests, all manually constructed.
- `tests/components/test_literalfield.py` has 8 tests, all manually constructed.
- `tests/components/test_datetimefield.py` has 13 tests, all manually constructed.
- Field constructors: `FloatField(size, starting_position, decimal_digits, format, sep, value)`, `IntegerField(size, starting_position, value)`, `LiteralField(size, starting_position, value)`, `DatetimeField(size, starting_position, format, value)`.
- The `Field.write(line)` method returns a string (or bytes) of length `max(len(line), ending_position)` with the field value written at `[starting_position:ending_position]`.
- The `Field.read(line)` method reads from `[starting_position:ending_position]` and sets `self._value`.
- FloatField has complex formatting: format "F" (fixed), "E"/"e" (scientific), "D"/"d" (Fortran-style scientific with "D" instead of "E"), and a `sep` parameter for decimal separator.

## Specification

### Requirements

1. Create `tests/components/test_field_hypothesis.py` (single file for all field types) containing:
   - Hypothesis `@composite` strategies for each field type that generate valid `(field_instance, value)` pairs.
   - Property tests verifying the textual round-trip: `field.write("") -> line -> field.read(line) -> recovered_value == original_value`.
   - Property tests verifying the binary round-trip for IntegerField and FloatField (which support binary I/O with numpy dtypes).

2. Hypothesis strategies must generate:
   - **IntegerField**: `size` in `{2, 4, 8}` (matching `TYPES` dict), values within the numpy dtype range for that size, `starting_position=0`.
   - **FloatField**: `size` in `{4, 8}` for binary; for textual, `size` in `[3, 20]`, `decimal_digits` in `[0, min(10, size-1)]`, `format` in `["F", "f", "E", "e", "D", "d"]`, values in `[-99999, 99999]`. Only test the "else" branch (format "F" or zero values) for exact textual round-trip, since "E"/"D" non-zero uses truncation.
   - **LiteralField**: `size` in `[1, 80]`, values containing only printable ASCII characters (no control chars, no whitespace at edges since `_textual_read` strips).
   - **DatetimeField**: `size=10`, `format="%Y/%m/%d"`, dates between `datetime(1900, 1, 1)` and `datetime(2099, 12, 31)`.

3. Use `@settings(max_examples=200)` for field tests to balance thoroughness and CI runtime. Mark all hypothesis tests with `@pytest.mark.slow` since they take longer than unit tests.

4. The existing `test_floatfield_write_fuzz_equivalence` in `test_floatfield.py` must NOT be removed or modified. The hypothesis tests supplement it, they do not replace it.

### Inputs/Props

- No external inputs. Strategies generate values internally.

### Outputs/Behavior

- `tests/components/test_field_hypothesis.py` with 6-8 property-based test functions.

### Error Handling

- Hypothesis's `assume()` should be used to filter out values that cannot round-trip due to known limitations (e.g., FloatField format "E"/"D" non-zero truncation, values that overflow the field width).
- The `@example()` decorator should pin known edge cases: zero, negative zero, boundary values.

## Acceptance Criteria

- [ ] Given the file `tests/components/test_field_hypothesis.py` is created, when `pytest tests/components/test_field_hypothesis.py -v` is executed, then all tests pass with exit code 0.
- [ ] Given `test_integerfield_textual_roundtrip` runs with hypothesis, when 200 examples are generated, then for each example `IntegerField.read(IntegerField.write(""))` recovers the original integer value exactly.
- [ ] Given `test_floatfield_textual_roundtrip_f_format` runs with hypothesis, when 200 examples are generated, then for each example with format "F" `FloatField.read(FloatField.write(""))` recovers the original float value within `1e-{decimal_digits}` tolerance.
- [ ] Given `test_literalfield_textual_roundtrip` runs with hypothesis, when 200 examples are generated, then for each example `LiteralField.read(LiteralField.write(""))` recovers the original string value exactly after stripping.
- [ ] Given `test_datetimefield_textual_roundtrip` runs with hypothesis, when 200 examples are generated, then for each example `DatetimeField.read(DatetimeField.write(""))` recovers the original datetime value exactly.
- [ ] Given the full test suite is executed with `pytest tests/`, when all tests run, then all existing 392+ tests plus the new hypothesis tests pass with exit code 0.
- [ ] Given `ruff check tests/components/test_field_hypothesis.py` is executed, then zero violations are reported.

## Implementation Guide

### Suggested Approach

1. Create `tests/components/test_field_hypothesis.py` with imports:

   ```python
   from datetime import datetime
   import numpy as np
   import pytest
   from hypothesis import given, settings, assume, example
   from hypothesis import strategies as st
   from cfinterface.components.integerfield import IntegerField
   from cfinterface.components.floatfield import FloatField
   from cfinterface.components.literalfield import LiteralField
   from cfinterface.components.datetimefield import DatetimeField
   ```

2. Define strategies:

   ```python
   # IntegerField strategy: size determines numpy dtype and value range
   @st.composite
   def integer_field_args(draw):
       size = draw(st.sampled_from([2, 4, 8]))
       dtype = {2: np.int16, 4: np.int32, 8: np.int64}[size]
       info = np.iinfo(dtype)
       # Constrain to values that fit in `size` textual characters
       text_max = 10 ** (size - 1) - 1
       text_min = -(10 ** (size - 2) - 1) if size > 1 else 0
       lo = max(info.min, text_min)
       hi = min(info.max, text_max)
       value = draw(st.integers(min_value=lo, max_value=hi))
       return size, value
   ```

3. Write property tests for each field type. Example pattern for IntegerField:

   ```python
   @pytest.mark.slow
   @settings(max_examples=200)
   @given(args=integer_field_args())
   def test_integerfield_textual_roundtrip(args):
       size, value = args
       field = IntegerField(size, 0, value=value)
       line = field.write("")
       field2 = IntegerField(size, 0)
       field2.read(line)
       assert field2.value == value
   ```

4. For FloatField textual round-trip, restrict to format "F" and values that fit within the field width. Use `assume()` to skip cases where the formatted value overflows:

   ```python
   @st.composite
   def float_field_f_args(draw):
       size = draw(st.integers(min_value=5, max_value=16))
       dec = draw(st.integers(min_value=1, max_value=min(6, size - 2)))
       value = draw(st.floats(min_value=-9999, max_value=9999,
                              allow_nan=False, allow_infinity=False))
       return size, dec, value
   ```

5. For LiteralField, generate printable strings that do not start/end with whitespace (since `_textual_read` strips):

   ```python
   @st.composite
   def literal_field_args(draw):
       size = draw(st.integers(min_value=1, max_value=40))
       # Generate string of exactly `size` chars, no leading/trailing whitespace
       value = draw(st.text(
           alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")),
           min_size=1, max_size=size
       ))
       return size, value
   ```

6. For DatetimeField, generate dates within a safe range:

   ```python
   @pytest.mark.slow
   @settings(max_examples=200)
   @given(dt=st.datetimes(
       min_value=datetime(1900, 1, 1),
       max_value=datetime(2099, 12, 31)
   ))
   def test_datetimefield_textual_roundtrip(dt):
       dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
       field = DatetimeField(10, 0, format="%Y/%m/%d", value=dt)
       line = field.write("")
       field2 = DatetimeField(10, 0, format="%Y/%m/%d")
       field2.read(line)
       assert field2.value == dt
   ```

7. Add binary round-trip tests for IntegerField and FloatField using numpy dtype sizes.

### Key Files to Modify

- `tests/components/test_field_hypothesis.py` (CREATE)

### Patterns to Follow

- Follow the existing test naming convention: `test_{fieldtype}_{property}`.
- Use `@pytest.mark.slow` on all hypothesis tests, matching the marker registered in `pyproject.toml`.
- Use `@settings(max_examples=200)` as the standard for this project's hypothesis tests.
- Use `@st.composite` for strategies that need to draw correlated values (e.g., size determines value range).

### Pitfalls to Avoid

- Do NOT test FloatField "E"/"D" non-zero textual round-trip -- the implementation uses truncation (`value[:self.size]`) which is lossy by design. Only test format "F" for textual round-trip, and "E"/"D" only for zero values.
- Do NOT modify `test_floatfield.py` -- the existing fuzz test stays as-is.
- Do NOT use `@settings(max_examples=...)` values above 500 -- CI must complete in reasonable time.
- Do NOT generate LiteralField values with leading/trailing whitespace -- `_textual_read` strips, so this would fail round-trip by design.
- Do NOT generate FloatField values with NaN or Infinity -- these have special handling that bypasses the normal write path.

## Testing Requirements

### Unit Tests

The hypothesis tests ARE the deliverable. They exercise the round-trip property for each field type across hundreds of random inputs.

### Integration Tests

Not applicable -- field round-trips are unit-level by nature.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-006-add-py-typed-and-dev-deps.md (hypothesis must be installed), ticket-011-create-conftest-and-fixtures.md (fixture infrastructure in place)
- **Blocks**: None

## Effort Estimate

**Points**: 3
**Confidence**: High
