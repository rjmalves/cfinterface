# ticket-022 Create TabularSection Convenience Base Class

## Context

### Background

With the `TabularParser` engine from ticket-021 in place, consumer packages still need to wire up the parser inside a `Section.read()` / `Section.write()` override. Looking at inewave's tabular Section implementations (e.g., `BlocoDuracaoPatamar` in `inewave/newave/modelos/patamar.py`), every one follows the same pattern:

1. In `__init__`, define a `Line` with fields
2. In `read()`, skip header lines, loop `file.readline()` until an end condition, call `line.read()` on each, accumulate into numpy array, convert to DataFrame
3. In `write()`, iterate over the DataFrame rows, call `line.write()` on each, write to file

A `TabularSection` base class can reduce this ~50-line boilerplate to ~10 lines by providing declarative class attributes (`COLUMNS`, `HEADER_LINES`, `END_PATTERN`) and implementing `read()`/`write()` once.

### Relation to Epic

This is the second ticket in epic-06. It depends on ticket-021 (TabularParser) and provides the consumer-facing API that makes tabular Section definitions trivial. Ticket-023 (delimited parsing) extends the parser that this class uses.

### Current State

- `cfinterface/components/section.py` -- `Section` base class with `read(file, *args, **kwargs)`, `write(file, *args, **kwargs)`, `data` property, `__slots__`, back-reference slots (`_container`, `_index`, fallbacks)
- `cfinterface/components/tabular.py` -- `TabularParser` and `ColumnDef` (created in ticket-021). `TabularParser` has `parse_lines(lines)` returning `Dict[str, List[Any]]` and `format_rows(data)` returning `List[str]`
- `cfinterface/components/defaultsection.py` -- `DefaultSection(Section)` provides the pattern for a concrete Section subclass in cfinterface itself
- Consumer pattern: Sections store parsed data in `self.data` (via the `Section.data` property setter)
- `Section.STORAGE` class attribute defaults to `StorageType.TEXT`

## Specification

### Requirements

1. Create `TabularSection` class in `cfinterface/components/tabular.py` (same file as `TabularParser`):
   - Extends `Section`
   - Provides declarative class-level attributes for tabular format definition
   - Implements `read()` and `write()` using `TabularParser`

2. Class-level attributes (set by subclasses):
   - `COLUMNS: List[ColumnDef] = []` -- column specification (mandatory in subclasses)
   - `HEADER_LINES: int = 0` -- number of header lines to skip before tabular data starts
   - `END_PATTERN: str = ""` -- regex pattern that marks the end of tabular data. Empty string means read until EOF or empty line.
   - `STORAGE: Union[str, StorageType] = StorageType.TEXT` -- inherited from Section

3. `__init__(self, previous=None, next=None, data=None)`:
   - Call `super().__init__(previous, next, data)`
   - Create `TabularParser(self.__class__.COLUMNS, storage=self.__class__.STORAGE)` and store as `self._parser`
   - Store header lines for write-back in `self._headers: List[str]`

4. `read(self, file: IO, *args, **kwargs) -> bool`:
   - Read and store `HEADER_LINES` lines from file (for write-back fidelity)
   - Read data lines until: `END_PATTERN` is matched (if non-empty), or empty line (`len(line) <= 1`), or EOF (`line == ""`)
   - When `END_PATTERN` matches, seek back to before the matching line (so the caller can still process it) -- this matches the pattern used in `BlocoDuracaoPatamar.read()`
   - Pass accumulated data lines to `self._parser.parse_lines()`
   - Store result in `self.data`
   - Return `True`

5. `write(self, file: IO, *args, **kwargs) -> bool`:
   - Write stored header lines back to file
   - Call `self._parser.format_rows(self.data)` to get formatted lines
   - Write each formatted line to file
   - Return `True`

6. `__eq__` implementation:
   - Compare by checking both are same class and `self.data == o.data` (dict equality for dict-of-lists)

### Inputs/Props

- Subclass sets `COLUMNS`, `HEADER_LINES`, `END_PATTERN` as class attributes
- `read()` takes an `IO` file object positioned at the start of the section
- `write()` takes an `IO` file object to write to
- `self.data` is `Dict[str, List[Any]]` (the dict-of-lists from TabularParser)

### Outputs/Behavior

- After `read()`, `self.data` contains a `Dict[str, List[Any]]` with column names as keys
- After `write()`, the file contains the header lines followed by formatted data lines
- `self.empty` returns `True` when `self.data is None` (inherited from Section)

### Error Handling

- If `COLUMNS` is empty (subclass forgot to set it), `read()` returns `True` with `self.data` as an empty dict -- no crash, the parser handles empty columns gracefully
- If `self.data` is `None` when `write()` is called, write only the headers (if any) -- consistent with how other components handle empty data
- The END_PATTERN regex matching uses the `_compile()` / `_pattern_cache` from `cfinterface/adapters/components/repository.py` for consistency with the Block pattern matching

## Acceptance Criteria

- [ ] Given a `TabularSection` subclass with `COLUMNS = [ColumnDef("year", IntegerField(4, 0)), ColumnDef("value", FloatField(8, 5, 2))]` and `HEADER_LINES = 1`, when `read()` is called on a file with 1 header + 3 data lines + empty line, then `self.data` is a dict with keys `["year", "value"]` each having 3 elements
- [ ] Given the same subclass, when `write()` is called with the data from `read()`, then the output matches the original file content (round-trip fidelity)
- [ ] Given a subclass with `END_PATTERN = "TOTAL"`, when `read()` encounters a line matching "TOTAL", then it stops reading, seeks back, and `self.data` contains only the rows before the matching line
- [ ] Given a subclass with `HEADER_LINES = 2`, when `read()` then `write()` is called, then the 2 header lines are preserved exactly in the output
- [ ] Given a subclass with no data (empty file after headers), when `read()` is called, then `self.data` is an empty dict-of-lists with correct keys
- [ ] Given `self.data is None`, when `write()` is called, then only headers are written (no crash)
- [ ] `TabularSection` is importable from `cfinterface.components.tabular` and re-exported from `cfinterface.components`
- [ ] `TabularSection.__eq__` compares data correctly between two instances of the same subclass
- [ ] All new code passes `ruff check` and `ruff format --check`
- [ ] At least 8 new tests are added

## Implementation Guide

### Suggested Approach

1. Add `TabularSection` class to `cfinterface/components/tabular.py` after the `TabularParser` class
2. Define class attributes:

   ```python
   class TabularSection(Section):
       __slots__ = ["_parser", "_headers"]

       COLUMNS: List[ColumnDef] = []
       HEADER_LINES: int = 0
       END_PATTERN: str = ""
   ```

3. Implement `__init__`:
   ```python
   def __init__(self, previous=None, next=None, data=None) -> None:
       super().__init__(previous, next, data)
       self._parser = TabularParser(
           self.__class__.COLUMNS,
           storage=self.__class__.STORAGE,
       )
       self._headers: List[str] = []
   ```
4. Implement `read()`:

   ```python
   def read(self, file: IO, *args, **kwargs) -> bool:
       self._headers = []
       for _ in range(self.__class__.HEADER_LINES):
           self._headers.append(file.readline())

       lines: List[str] = []
       end_pattern = self.__class__.END_PATTERN
       while True:
           pos = file.tell()
           line = file.readline()
           if line == "" or len(line) <= 1:
               break
           if end_pattern and re.search(end_pattern, line):
               file.seek(pos)
               break
           lines.append(line)

       self.data = self._parser.parse_lines(lines)
       return True
   ```

5. Implement `write()`:
   ```python
   def write(self, file: IO, *args, **kwargs) -> bool:
       for header in self._headers:
           file.write(header)
       if self.data is not None:
           for line in self._parser.format_rows(self.data):
               file.write(line)
       return True
   ```
6. Implement `__eq__`:
   ```python
   def __eq__(self, o: object) -> bool:
       if not isinstance(o, self.__class__):
           return False
       return self.data == o.data
   ```
7. Update `cfinterface/components/__init__.py` to add `TabularSection` to the imports (alongside `TabularParser` and `ColumnDef` from ticket-021)
8. Add tests in `tests/components/test_tabular.py` (append to the file created in ticket-021)

### Key Files to Modify

- `cfinterface/components/tabular.py` -- add `TabularSection` class
- `cfinterface/components/__init__.py` -- add `TabularSection` re-export
- `tests/components/test_tabular.py` -- append TabularSection tests

### Patterns to Follow

- `Section.__init__` call chain: `super().__init__(previous, next, data)` -- same as `DefaultSection`
- `__slots__` must include `_parser` and `_headers` -- consistent with all component classes using `__slots__`
- Do NOT add `_container`, `_index`, fallback slots -- they are inherited from `Section.__slots__`
- `read(file, *args, **kwargs)` and `write(file, *args, **kwargs)` signature matches the Section base class exactly
- Use `re.search()` for END_PATTERN matching -- same as how `Block.begins()` / `Block.ends()` delegates to `factory(storage).begins()` which uses regex. Import `re` at module level since it is stdlib.
- File seek-back pattern on end-pattern: `pos = file.tell()` before readline, `file.seek(pos)` if pattern matches -- copied from `BlocoDuracaoPatamar.read()` in inewave
- Header preservation for write-back: store raw header lines in `self._headers` -- same pattern as inewave sections that store `self.__cabecalhos`

### Pitfalls to Avoid

- Do NOT add `"data"` to `__slots__` -- the `data` property is defined on `Section` via `__data` (name-mangled). Adding it to subclass slots would shadow the property.
- Do NOT assume `self.data` is always a dict -- it could be `None` (empty section). Check before calling `format_rows()`.
- `file.readline()` returns `""` at EOF but returns `"\n"` for blank lines. Use `line == ""` for EOF detection and `len(line) <= 1` for blank lines (matching inewave convention).
- The `_headers` slot stores the raw lines including `\n` so they can be written back verbatim.

## Testing Requirements

### Unit Tests

Append to `tests/components/test_tabular.py`:

1. `test_tabular_section_read_basic` -- define a subclass with 2 COLUMNS and HEADER_LINES=1, read from mock file, verify data
2. `test_tabular_section_write_basic` -- write data to mock file, verify output matches expected
3. `test_tabular_section_round_trip` -- read then write, compare output to input
4. `test_tabular_section_end_pattern` -- subclass with END_PATTERN, verify reading stops at pattern and file position is seeked back
5. `test_tabular_section_empty_data` -- read from file with only headers + empty line, verify empty dict-of-lists
6. `test_tabular_section_write_none_data` -- set data to None, call write, verify only headers are written
7. `test_tabular_section_header_preservation` -- verify header lines are preserved exactly through read/write cycle
8. `test_tabular_section_equality` -- two instances with same data are equal; different data are not equal; different class is not equal

### Integration Tests

None required.

### E2E Tests (if applicable)

None.

## Dependencies

- **Blocked By**: ticket-021
- **Blocks**: None (ticket-023 extends TabularParser, not TabularSection)

## Effort Estimate

**Points**: 2
**Confidence**: High
