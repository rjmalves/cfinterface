# ticket-021 Implement TabularParser Core Engine

## Context

### Background

Consumer packages like inewave contain dozens of Section and Block subclasses that parse tabular (row-of-fields) data from files. Each subclass reimplements the same loop: read lines, apply a `Line` to extract field values, accumulate rows into a numpy array, then convert to a DataFrame. The `ValoresSerie` block in `inewave/nwlistop/modelos/blocos/valoresserie.py` is the canonical example: it defines a `DATA_LINE`, loops over `file.readline()`, calls `self.__linha.read(linha)`, accumulates into a pre-allocated `np.zeros` array, and finally calls `pd.DataFrame(tabela, columns=cols)`. The `BlocoDuracaoPatamar` in `inewave/newave/modelos/patamar.py` follows the identical pattern with different field layouts.

This ticket creates a reusable `TabularParser` class that centralizes this read loop. The parser accepts a column specification (what fields each row contains) and transforms a sequence of text lines into a `dict[str, list[Any]]` -- a dict-of-lists keyed by column name. An optional `to_dataframe()` class method provides pandas conversion via lazy import.

### Relation to Epic

This is the foundation ticket for epic-06. It provides the core engine that ticket-022 (TabularSection convenience class) and ticket-023 (delimited parsing support) build upon.

### Current State

- `cfinterface/components/line.py` contains the `Line` class that already handles positional field extraction via `TextualRepository.read()`. A `Line` takes a list of `Field` instances and reads/writes them from a string.
- `cfinterface/components/field.py` has the `Field` base class with `_size`, `_starting_position`, `read(line)`, `write(line)`.
- Concrete fields: `IntegerField`, `FloatField`, `LiteralField`, `DatetimeField` -- all in `cfinterface/components/`.
- `cfinterface/_utils/__init__.py` has `_is_null(value)` for null checking.
- pandas is an optional dependency; numpy is the only hard runtime dependency.
- No `cfinterface/components/tabular.py` file exists yet.
- Test count: 292.

## Specification

### Requirements

1. Create a `ColumnDef` named tuple in `cfinterface/components/tabular.py`:
   - Fields: `name: str`, `field: Field` (a `Field` instance defining type, size, starting position)
   - This is the unit of column specification -- one `ColumnDef` per column in the table

2. Create a `TabularParser` class in `cfinterface/components/tabular.py`:
   - Constructor: `__init__(self, columns: List[ColumnDef], storage: Union[str, StorageType] = "")`
   - Internally creates a `Line` from the list of `ColumnDef.field` instances
   - Stores column names separately for dict-key mapping

3. `parse_lines(self, lines: List[str]) -> Dict[str, List[Any]]`:
   - Iterates over the provided lines
   - For each line, calls `self._line.read(line)` to get a `List[Any]` of field values
   - Accumulates values into a dict-of-lists keyed by column name
   - Returns the dict-of-lists

4. `format_rows(self, data: Dict[str, List[Any]]) -> List[str]`:
   - Inverse of `parse_lines`: takes a dict-of-lists and produces a list of formatted text lines
   - For each row index, assembles a values list and calls `self._line.write(values)` to produce a formatted string
   - Returns the list of formatted strings

5. Class method `to_dataframe(data: Dict[str, List[Any]]) -> "pd.DataFrame"`:
   - Static/classmethod that converts a dict-of-lists to a pandas DataFrame
   - Uses lazy pandas import: `try: import pandas as pd except ImportError: raise ImportError("pandas is required: pip install cfinterface[pandas]")`
   - Returns `pd.DataFrame(data)`

6. Error handling on malformed rows:
   - If `Line.read()` raises an exception on a line, catch it and fill the row with `None` for all columns
   - This is consistent with `Field.read()` which already catches `ValueError` and sets `self._value = None`

### Inputs/Props

- `columns: List[ColumnDef]` -- ordered list of column definitions. Each `ColumnDef` has `.name` (str) and `.field` (a `Field` instance)
- `storage: Union[str, StorageType]` -- storage type for the Line (default `""` for textual fallback, matching the existing `Line` convention)
- `lines: List[str]` -- raw text lines to parse (for `parse_lines`)
- `data: Dict[str, List[Any]]` -- dict-of-lists to format (for `format_rows`)

### Outputs/Behavior

- `parse_lines()` returns `Dict[str, List[Any]]` where keys are column names in the same order as the `columns` list, and each value is a list of parsed values (one per input line)
- `format_rows()` returns `List[str]` where each string is a formatted line (with trailing `\n`, matching `Line.write()` behavior)
- `to_dataframe()` returns a `pd.DataFrame` with column names from the keys

### Error Handling

- Malformed row: catch `Exception` during `Line.read()`, fill entire row with `None` values. Do NOT skip the row -- downstream consumers expect row counts to match.
- Empty input (`lines=[]`): return `{name: [] for name in column_names}` -- an empty dict-of-lists with the correct keys.
- `to_dataframe()` when pandas not installed: raise `ImportError` with install instructions.

## Acceptance Criteria

- [ ] Given a `TabularParser` with 3 columns (IntegerField, FloatField, LiteralField), when `parse_lines()` is called with 5 valid lines, then it returns a dict with 3 keys and each key maps to a list of length 5 with correctly typed values
- [ ] Given a `TabularParser` with 2 columns, when `parse_lines()` is called with an empty list, then it returns a dict with 2 keys each mapping to an empty list
- [ ] Given a `TabularParser`, when `parse_lines()` encounters a malformed line that causes a read error, then that row is filled with `None` for all columns and parsing continues
- [ ] Given a dict-of-lists produced by `parse_lines()`, when `format_rows()` is called, then the output lines can be re-parsed by `parse_lines()` to produce equivalent data (round-trip)
- [ ] Given a dict-of-lists, when `to_dataframe()` is called and pandas is installed, then it returns a DataFrame with the correct columns and data
- [ ] Given `to_dataframe()` is called when pandas is NOT installed, then it raises `ImportError` with a message containing "pip install cfinterface[pandas]"
- [ ] `ColumnDef` is a named tuple with fields `name` and `field`
- [ ] `TabularParser` and `ColumnDef` are importable from `cfinterface.components.tabular`
- [ ] `TabularParser` and `ColumnDef` are re-exported from `cfinterface.components.__init__`
- [ ] All new code passes `ruff check` and `ruff format --check`
- [ ] At least 10 new tests are added covering parse, format, round-trip, error handling, and the to_dataframe method

## Implementation Guide

### Suggested Approach

1. Create `cfinterface/components/tabular.py`
2. Define `ColumnDef = NamedTuple("ColumnDef", [("name", str), ("field", Field)])` -- use the functional `NamedTuple` form or class-based form, both are fine
3. Implement `TabularParser.__init__` -- store `columns`, create a `Line` from `[col.field for col in columns]` with the given `storage`
4. Implement `parse_lines()`:
   ```python
   def parse_lines(self, lines: List[str]) -> Dict[str, List[Any]]:
       names = [col.name for col in self._columns]
       result: Dict[str, List[Any]] = {name: [] for name in names}
       for line in lines:
           try:
               values = self._line.read(line)
           except Exception:
               values = [None] * len(self._columns)
           for name, val in zip(names, values):
               result[name].append(val)
       return result
   ```
5. Implement `format_rows()`:
   ```python
   def format_rows(self, data: Dict[str, List[Any]]) -> List[str]:
       names = [col.name for col in self._columns]
       n_rows = len(next(iter(data.values()))) if data else 0
       lines: List[str] = []
       for i in range(n_rows):
           values = [data[name][i] for name in names]
           lines.append(self._line.write(values))
       return lines
   ```
6. Implement `to_dataframe()` as a `@staticmethod`:
   ```python
   @staticmethod
   def to_dataframe(data: Dict[str, List[Any]]) -> "pd.DataFrame":
       try:
           import pandas as pd
       except ImportError:
           raise ImportError(
               "pandas is required for this operation. "
               "Install it with: pip install cfinterface[pandas]"
           )
       return pd.DataFrame(data)
   ```
7. Update `cfinterface/components/__init__.py` to add: `from .tabular import TabularParser, ColumnDef  # noqa`
8. Create tests in `tests/components/test_tabular.py`

### Key Files to Modify

- `cfinterface/components/tabular.py` -- **NEW** -- TabularParser and ColumnDef
- `cfinterface/components/__init__.py` -- add TabularParser, ColumnDef re-export
- `tests/components/test_tabular.py` -- **NEW** -- all tests

### Patterns to Follow

- Use `__slots__` on `TabularParser` (consistent with all component classes: `Section`, `Block`, `Register`, `Line`)
- Use one-line docstring for private helpers, numpydoc for public class and public methods
- Lazy pandas import pattern: `try: import pandas as pd except ImportError: raise ImportError(...)` inside the method body (established in epic-01, see `cfinterface/files/registerfile.py`)
- `Union[str, StorageType]` for storage parameter, default `""` (matching `Line.__init__` convention)
- Use the existing `Line` class for row parsing -- do NOT reimplement field extraction logic
- Field instances in `ColumnDef` should be fresh instances (not shared), because `Line.read()` mutates field values in place

### Pitfalls to Avoid

- Do NOT import pandas at module level -- it is an optional dependency
- Do NOT make TabularParser generic (learnings: "do NOT make Line or any new parser class generic")
- Do NOT create a new `cfinterface/parsers/` package -- put it in `cfinterface/components/tabular.py` alongside other component classes
- `Line.read()` mutates field values in place. If you need thread safety or re-entrancy, create the `Line` fresh per call. For the initial implementation, a single `Line` stored on `self._line` is fine since Section.read() calls are single-threaded.
- `Line.write()` returns a string that includes a trailing `\n` -- be aware of this in round-trip tests
- Field instances are position-specific. When creating a Line from ColumnDefs, the fields' `starting_position` and `size` attributes define where in the line each field is read from. The `ColumnDef` order must match the physical layout order.

## Testing Requirements

### Unit Tests

Create `tests/components/test_tabular.py` with at minimum:

1. `test_columndef_creation` -- ColumnDef is a named tuple with name and field attributes
2. `test_parse_lines_integer_columns` -- parse 3 lines with 2 IntegerField columns, verify correct int values
3. `test_parse_lines_mixed_columns` -- parse lines with IntegerField, FloatField, LiteralField columns
4. `test_parse_lines_empty_input` -- parse empty list, verify empty dict-of-lists with correct keys
5. `test_parse_lines_malformed_row` -- include a line that is too short, verify None fill
6. `test_format_rows_basic` -- format a dict-of-lists, verify output line count and content
7. `test_round_trip_integer_columns` -- parse lines, format back, re-parse, compare
8. `test_round_trip_mixed_columns` -- same with mixed field types
9. `test_to_dataframe_basic` -- verify DataFrame creation (skip if pandas not available in test env, but it should be since dev deps include pandas)
10. `test_to_dataframe_import_error` -- mock pandas import failure, verify ImportError message
11. `test_parser_column_names_property` -- verify column names are accessible
12. `test_parse_lines_single_column` -- edge case: one column only

### Integration Tests

None required -- the TabularParser is a self-contained component that composes with Line internally.

### E2E Tests (if applicable)

None.

## Dependencies

- **Blocked By**: None (tickets 002 and 017 are already completed)
- **Blocks**: ticket-022, ticket-023

## Effort Estimate

**Points**: 3
**Confidence**: High
