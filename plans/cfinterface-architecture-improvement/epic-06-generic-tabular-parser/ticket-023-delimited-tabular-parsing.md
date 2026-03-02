# ticket-023 Add Delimited Tabular Parsing Support

## Context

### Background

The `TabularParser` created in ticket-021 handles fixed-width positional parsing by leveraging the `Line` class. However, consumer packages like inewave also have delimited file formats (CSV-like), as seen in `TabelaMediassin` and `TabelaMediasree` in `inewave/nwlistop/modelos/mediassin.py` and `mediasree.py`. These sections currently use `pd.read_csv()` directly, bypassing cfinterface's field system entirely.

The `Line` class already has built-in delimiter support: its constructor accepts `delimiter: Optional[Union[str, bytes]]`, and `TextualRepository` has `__delimted_reading()` and `__delimted_writing()` methods that split/join on the delimiter. When a delimiter is set, `TextualRepository` adjusts each field to read from position 0 with size=field.size (i.e., reads the entire split token).

This ticket extends `TabularParser` to accept a delimiter parameter, which it passes through to the internal `Line`. This enables delimited tabular parsing using the same field type system (IntegerField, FloatField, etc.) for type conversion, instead of relying on raw `pd.read_csv()`.

### Relation to Epic

This is the third and final ticket in epic-06. It extends the `TabularParser` from ticket-021 with delimiter support. It does not modify `TabularSection` from ticket-022 directly, but TabularSection inherits the capability because it delegates to TabularParser.

### Current State

After ticket-021:

- `cfinterface/components/tabular.py` contains `ColumnDef`, `TabularParser`, and `TabularSection`
- `TabularParser.__init__` takes `columns: List[ColumnDef]` and `storage: Union[str, StorageType]`
- Internally, `TabularParser` creates `Line(fields, storage=storage)` and calls `Line.read(line)` / `Line.write(values)`

After ticket-022:

- `TabularSection` extends `Section` with declarative COLUMNS, HEADER_LINES, END_PATTERN

The existing `Line` class (in `cfinterface/components/line.py`):

- Constructor already accepts `delimiter: Optional[Union[str, bytes]] = None`
- `Line.read(line)` passes the delimiter to `TextualRepository.read(line, delimiter)`
- `Line.write(values)` passes the delimiter to `TextualRepository.write(values, delimiter)`
- When delimiter is set, `TextualRepository.__delimted_reading()` splits on delimiter, strips whitespace, then reads each field from the split token
- When delimiter is set, `TextualRepository.__delimted_writing()` writes each field to a blank string, strips, then joins with delimiter

## Specification

### Requirements

1. Add `delimiter: Optional[Union[str, bytes]] = None` parameter to `TabularParser.__init__`:
   - Pass it through to the internal `Line(fields, delimiter=delimiter, storage=storage)`
   - Store it as `self._delimiter` for introspection

2. Add `DELIMITER: Optional[Union[str, bytes]] = None` class attribute to `TabularSection`:
   - Thread it through to `TabularParser(columns, storage=storage, delimiter=self.__class__.DELIMITER)` in `TabularSection.__init__`

3. For delimited parsing, the `ColumnDef.field` starting_position is irrelevant (the delimiter determines column boundaries). The field's `size` is used by `TextualRepository.__positional_to_delimited_field()` to set the read width to the full token. Document this convention.

4. No changes needed to `parse_lines()` or `format_rows()` -- they already call `Line.read()` and `Line.write()`, which handle the delimiter internally.

5. Use Python's stdlib only -- do NOT use the `csv` module. The existing `TextualRepository.__delimted_reading()` already handles delimiter splitting with `line.split(delimiter)` and `.strip()`. This is sufficient for the file formats in the inewave ecosystem, which do not use quoted fields.

### Inputs/Props

- `delimiter: Optional[Union[str, bytes]]` -- the delimiter character/string. `None` means fixed-width (default). Common values: `";"`, `","`, `"\t"`, `" "`.
- On `TabularSection`, set as class attribute `DELIMITER`.

### Outputs/Behavior

- When `delimiter` is `None`: behavior is identical to ticket-021 (fixed-width positional parsing)
- When `delimiter` is set: each line is split on the delimiter, each token is stripped, and each field reads from the full token (starting_position is ignored, field reads from position 0 with size = field.size)
- `format_rows()` with a delimiter produces lines with fields joined by the delimiter character, consistent with `TextualRepository.__delimted_writing()`

### Error Handling

- If a line has fewer tokens than columns after splitting on the delimiter, the remaining fields will attempt to read from empty strings. `Field.read()` catches `ValueError` and sets `value = None`, so missing columns become `None`. This is consistent with the malformed-row handling from ticket-021.
- Empty tokens (e.g., `";;;"` with `";"` delimiter) are handled by `Field.read()` -- each field type handles empty/whitespace input by returning `None` via the `ValueError` catch.

## Acceptance Criteria

- [ ] Given a `TabularParser` with `delimiter=";"` and 3 columns, when `parse_lines()` is called with semicolon-separated lines, then values are correctly parsed with proper types
- [ ] Given a `TabularParser` with `delimiter=","` and FloatField columns, when `parse_lines()` is called with `"1.5, 2.3, 3.7\n"`, then values are `[1.5, 2.3, 3.7]` (whitespace stripped)
- [ ] Given a `TabularParser` with `delimiter=None` (default), behavior is identical to fixed-width positional parsing from ticket-021 (regression check)
- [ ] Given a delimited line with fewer tokens than columns, then missing columns are filled with `None`
- [ ] Given a `TabularSection` subclass with `DELIMITER = ";"`, when `read()` is called on a semicolon-delimited file, then `self.data` contains correctly parsed dict-of-lists
- [ ] Given delimited data, when `format_rows()` is called, then the output uses the delimiter to join fields
- [ ] Round-trip: delimited parse then format produces equivalent data when re-parsed
- [ ] `TabularParser.delimiter` property is accessible for introspection
- [ ] All new code passes `ruff check` and `ruff format --check`
- [ ] At least 8 new tests are added covering delimited parsing, formatting, round-trip, and edge cases

## Implementation Guide

### Suggested Approach

1. Modify `TabularParser.__init__` in `cfinterface/components/tabular.py`:

   ```python
   def __init__(
       self,
       columns: List[ColumnDef],
       storage: Union[str, StorageType] = "",
       delimiter: Optional[Union[str, bytes]] = None,
   ) -> None:
       self._columns = columns
       self._delimiter = delimiter
       self._line = Line(
           [col.field for col in columns],
           delimiter=delimiter,
           storage=storage,
       )
   ```

   This is a backward-compatible change -- existing callers that don't pass `delimiter` get `None` (fixed-width).

2. Add a `delimiter` property to `TabularParser`:

   ```python
   @property
   def delimiter(self) -> Optional[Union[str, bytes]]:
       return self._delimiter
   ```

3. Add `DELIMITER` class attribute to `TabularSection`:

   ```python
   class TabularSection(Section):
       __slots__ = ["_parser", "_headers"]

       COLUMNS: List[ColumnDef] = []
       HEADER_LINES: int = 0
       END_PATTERN: str = ""
       DELIMITER: Optional[Union[str, bytes]] = None
   ```

4. Update `TabularSection.__init__` to pass the delimiter:

   ```python
   def __init__(self, previous=None, next=None, data=None) -> None:
       super().__init__(previous, next, data)
       self._parser = TabularParser(
           self.__class__.COLUMNS,
           storage=self.__class__.STORAGE,
           delimiter=self.__class__.DELIMITER,
       )
       self._headers: List[str] = []
   ```

5. Add tests to `tests/components/test_tabular.py`

### Key Files to Modify

- `cfinterface/components/tabular.py` -- add `delimiter` parameter to `TabularParser.__init__`, add `delimiter` property, add `DELIMITER` to `TabularSection`
- `tests/components/test_tabular.py` -- append delimited parsing tests

### Patterns to Follow

- `Optional[Union[str, bytes]]` for delimiter type -- matches `Line.__init__` signature exactly
- `None` default for delimiter -- matches `Line.__init__` convention (None = positional, not delimited)
- For delimited ColumnDef fields, use `starting_position=0` by convention (the position is irrelevant for delimited parsing, but the field constructor requires it). Use `size` to set the maximum expected token width. Example:
  ```python
  ColumnDef("name", LiteralField(size=20, starting_position=0))
  ColumnDef("value", FloatField(size=10, starting_position=0, decimal_digits=2))
  ```
- Do NOT modify `Line`, `TextualRepository`, or any existing class -- the delimiter support is already fully implemented there

### Pitfalls to Avoid

- Do NOT use Python's `csv` module -- the existing `TextualRepository.__delimted_reading()` uses `line.split(delimiter)` which is simpler and matches the inewave file format conventions (no quoted fields)
- Do NOT handle multi-character delimiters specially -- `str.split()` already handles multi-character delimiters correctly
- When testing delimited parsing, remember that `Line.write()` with a delimiter still appends `\n`. Account for this in assertions.
- For delimited ColumnDefs, the `field.size` still matters for formatting: `TextualRepository.__delimted_writing()` calls `field.write("")` then `.strip()`, so the field size determines the internal formatting width before stripping. Use a size large enough to hold the formatted value.
- Do NOT change the default behavior of `TabularParser` -- when `delimiter=None`, everything must work exactly as before (regression safety)

## Testing Requirements

### Unit Tests

Append to `tests/components/test_tabular.py`:

1. `test_parse_lines_semicolon_delimited` -- 3 columns, semicolon delimiter, 3 data lines, verify correct values
2. `test_parse_lines_comma_delimited` -- 2 FloatField columns, comma delimiter, verify float parsing
3. `test_parse_lines_tab_delimited` -- tab delimiter with LiteralField and IntegerField
4. `test_parse_lines_delimited_missing_tokens` -- line with fewer tokens than columns, verify None fill
5. `test_format_rows_delimited` -- format a dict-of-lists with semicolon delimiter, verify output uses semicolon
6. `test_round_trip_delimited` -- parse semicolon-delimited lines, format back, re-parse, compare
7. `test_delimiter_none_is_positional` -- verify that delimiter=None gives same results as ticket-021 tests (regression)
8. `test_tabular_section_delimited` -- TabularSection subclass with DELIMITER=";", read from mock file, verify data
9. `test_parser_delimiter_property` -- verify `parser.delimiter` returns the configured delimiter

### Integration Tests

None required.

### E2E Tests (if applicable)

None.

## Dependencies

- **Blocked By**: ticket-021
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
