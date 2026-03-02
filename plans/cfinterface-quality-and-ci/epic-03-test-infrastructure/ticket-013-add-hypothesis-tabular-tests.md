# ticket-013 Add Hypothesis Property-Based Tests for TabularParser Round-Trips

## Context

### Background

The `TabularParser` class in `cfinterface/components/tabular.py` supports both fixed-width positional parsing and delimiter-separated parsing. It transforms lists of text lines into a dict-of-lists and provides the inverse `format_rows()` operation. The existing `tests/components/test_tabular.py` has comprehensive manually-written tests (49 tests) covering fixed-width, delimited, round-trip, and edge cases. However, it does not use property-based testing to explore the input space systematically.

The key round-trip property for `TabularParser` is: `parse_lines(format_rows(parse_lines(lines))) == parse_lines(lines)` for well-formed input. This must hold for both fixed-width and delimiter-separated modes.

### Relation to Epic

This is the third ticket in Epic 03. It extends property-based testing from individual fields (ticket-012) to the composite `TabularParser`, which orchestrates multiple fields to parse/format tabular data. It depends on ticket-011 for shared conftest fixtures and benefits from field-level strategies established in ticket-012.

### Current State

- `tests/components/test_tabular.py` has 49 hand-written tests covering `TabularParser`, `ColumnDef`, and `TabularSection`.
- `TabularParser.__init__` takes `columns: list[ColumnDef]`, `storage: str | StorageType = ""`, and `delimiter: str | bytes | None = None`.
- `ColumnDef` is a `NamedTuple` with fields `name: str` and `field: Field`.
- `TabularParser.parse_lines(lines)` returns `dict[str, list[Any]]`.
- `TabularParser.format_rows(data)` returns `list[str]` (each ending with `\n`).
- Fixed-width mode: each field's `starting_position` and `size` determine where it reads/writes.
- Delimited mode: `str.split(delimiter)` splits the line into tokens; each token is passed to the field at position 0 with the token's length.
- `TabularParser` uses `__slots__ = ["_columns", "_delimiter", "_line"]`.
- Round-trip for formatted data (not original text) is the reliable property: `parse(format(data)) == data` when data values are valid.

## Specification

### Requirements

1. Create `tests/components/test_tabular_hypothesis.py` containing:
   - A `@st.composite` strategy that generates a `TabularParser` with 1-4 integer columns at non-overlapping fixed-width positions, along with a matching data dict containing valid integer values.
   - A `@st.composite` strategy that generates a `TabularParser` with 1-3 columns of mixed types (IntegerField, FloatField format "F", LiteralField) at non-overlapping positions, along with matching data.
   - A `@st.composite` strategy that generates a delimiter-separated `TabularParser` with 1-3 columns and matching data.
   - Property test: `parse_lines(format_rows(data)) == data` for integer-only parsers.
   - Property test: `parse_lines(format_rows(data)) == data` (with float tolerance) for mixed-type parsers.
   - Property test: `parse_lines(format_rows(data)) == data` for delimiter-separated parsers.

2. All hypothesis tests must use `@settings(max_examples=200)` and be marked `@pytest.mark.slow`.

3. The existing `test_tabular.py` must NOT be modified.

### Inputs/Props

- No external inputs. Strategies generate parsers and data internally.

### Outputs/Behavior

- `tests/components/test_tabular_hypothesis.py` with 3-4 property-based test functions.

### Error Handling

- Use `assume()` to filter out data combinations that are known to not round-trip cleanly (e.g., float values that overflow the field width, literal values with leading/trailing whitespace).

## Acceptance Criteria

- [ ] Given the file `tests/components/test_tabular_hypothesis.py` is created, when `pytest tests/components/test_tabular_hypothesis.py -v` is executed, then all tests pass with exit code 0.
- [ ] Given `test_integer_parser_roundtrip` runs with hypothesis, when 200 examples are generated, then for each example `parse_lines(format_rows(data))` produces a dict equal to the original data dict for all integer columns.
- [ ] Given `test_mixed_parser_roundtrip` runs with hypothesis, when 200 examples are generated, then for each example integer and literal columns match exactly and float columns match within `1e-{decimal_digits}` tolerance.
- [ ] Given `test_delimited_parser_roundtrip` runs with hypothesis, when 200 examples are generated, then for each example `parse_lines(format_rows(data))` produces a dict matching the original data for all columns.
- [ ] Given the full test suite is executed with `pytest tests/`, when all tests run, then all existing tests plus the new hypothesis tests pass with exit code 0.
- [ ] Given `ruff check tests/components/test_tabular_hypothesis.py` is executed, then zero violations are reported.

## Implementation Guide

### Suggested Approach

1. Create `tests/components/test_tabular_hypothesis.py` with imports:

   ```python
   import pytest
   from hypothesis import given, settings, assume
   from hypothesis import strategies as st

   from cfinterface.components.floatfield import FloatField
   from cfinterface.components.integerfield import IntegerField
   from cfinterface.components.literalfield import LiteralField
   from cfinterface.components.tabular import ColumnDef, TabularParser
   ```

2. Define a strategy for integer-only parsers with non-overlapping columns:

   ```python
   @st.composite
   def integer_parser_with_data(draw):
       n_cols = draw(st.integers(min_value=1, max_value=4))
       col_size = 8  # fixed width per column
       columns = []
       for i in range(n_cols):
           name = f"col_{i}"
           field = IntegerField(col_size, i * col_size)
           columns.append(ColumnDef(name, field))
       parser = TabularParser(columns)
       n_rows = draw(st.integers(min_value=1, max_value=10))
       max_val = 10 ** (col_size - 1) - 1
       data = {}
       for col in columns:
           data[col.name] = draw(
               st.lists(
                   st.integers(min_value=0, max_value=max_val),
                   min_size=n_rows, max_size=n_rows
               )
           )
       return parser, data
   ```

3. Define a strategy for mixed-type parsers (IntegerField + FloatField "F" + LiteralField):

   ```python
   @st.composite
   def mixed_parser_with_data(draw):
       # Fixed layout: int(6) + float(10, dec=2) + literal(8)
       columns = [
           ColumnDef("id", IntegerField(6, 0)),
           ColumnDef("value", FloatField(10, 6, decimal_digits=2, format="F")),
           ColumnDef("label", LiteralField(8, 16)),
       ]
       parser = TabularParser(columns)
       n_rows = draw(st.integers(min_value=1, max_value=10))
       ids = draw(st.lists(
           st.integers(min_value=0, max_value=99999),
           min_size=n_rows, max_size=n_rows
       ))
       values = draw(st.lists(
           st.floats(min_value=-999, max_value=9999,
                     allow_nan=False, allow_infinity=False),
           min_size=n_rows, max_size=n_rows
       ))
       labels = draw(st.lists(
           st.text(
               alphabet=st.characters(
                   whitelist_categories=("L", "N")
               ),
               min_size=1, max_size=8
           ),
           min_size=n_rows, max_size=n_rows
       ))
       return parser, {"id": ids, "value": values, "label": labels}
   ```

4. Define a strategy for delimiter-separated parsers:

   ```python
   @st.composite
   def delimited_parser_with_data(draw):
       delimiter = draw(st.sampled_from([";", ",", "\t"]))
       n_cols = draw(st.integers(min_value=1, max_value=3))
       columns = []
       for i in range(n_cols):
           columns.append(ColumnDef(
               f"col_{i}", IntegerField(8, 0)
           ))
       parser = TabularParser(columns, delimiter=delimiter)
       n_rows = draw(st.integers(min_value=1, max_value=10))
       data = {}
       for col in columns:
           data[col.name] = draw(
               st.lists(
                   st.integers(min_value=0, max_value=9999999),
                   min_size=n_rows, max_size=n_rows
               )
           )
       return parser, data
   ```

5. Write the property tests:

   ```python
   @pytest.mark.slow
   @settings(max_examples=200)
   @given(args=integer_parser_with_data())
   def test_integer_parser_roundtrip(args):
       parser, data = args
       formatted = parser.format_rows(data)
       reparsed = parser.parse_lines(
           [ln.rstrip("\n") for ln in formatted]
       )
       assert reparsed == data
   ```

6. For the mixed-type round-trip, compare integers and labels exactly, floats with tolerance:
   ```python
   @pytest.mark.slow
   @settings(max_examples=200)
   @given(args=mixed_parser_with_data())
   def test_mixed_parser_roundtrip(args):
       parser, data = args
       formatted = parser.format_rows(data)
       reparsed = parser.parse_lines(
           [ln.rstrip("\n") for ln in formatted]
       )
       assert reparsed["id"] == data["id"]
       for v1, v2 in zip(reparsed["value"], data["value"]):
           assert abs(v1 - v2) < 0.01  # decimal_digits=2
       assert reparsed["label"] == data["label"]
   ```

### Key Files to Modify

- `tests/components/test_tabular_hypothesis.py` (CREATE)

### Patterns to Follow

- Follow the same testing patterns as `tests/components/test_tabular.py`: use local helper functions for parser construction, use `rstrip("\n")` before re-parsing formatted lines (as done in `test_round_trip_integer_columns`).
- Use `@st.composite` for strategies that need correlated draws.
- Use `@pytest.mark.slow` on all hypothesis tests.

### Pitfalls to Avoid

- Do NOT modify `tests/components/test_tabular.py`.
- Do NOT attempt to test that original raw text lines survive round-trip -- only test that the _data_ round-trips through `format_rows` then `parse_lines`.
- Do NOT generate LiteralField values containing the delimiter character when testing delimited mode -- this would break `str.split(delimiter)` since quoted fields are not supported.
- Do NOT generate float values with NaN or Infinity for round-trip tests.
- Remember that `format_rows` appends `\n` to each line, so strip it before passing to `parse_lines` in fixed-width mode (delimited mode strips newlines via the split operation).

## Testing Requirements

### Unit Tests

The hypothesis tests ARE the deliverable. They exercise the tabular round-trip property across varied column configurations, data sizes, and value ranges.

### Integration Tests

Not applicable.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-006-add-py-typed-and-dev-deps.md (hypothesis must be installed), ticket-011-create-conftest-and-fixtures.md (fixture infrastructure), ticket-012-add-hypothesis-field-tests.md (field strategies may inform approach)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
