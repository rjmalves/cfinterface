# ticket-023 Add Delimited Tabular Parsing Support

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Extend the `TabularParser` to support delimited formats (semicolon, comma, tab, space-separated) in addition to fixed-width positional parsing, so that consumers with CSV-like file formats can also use the generic parser.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/parsers/tabular.py`, `tests/parsers/test_tabular.py`
- **Key decisions needed**:
  - Whether delimiter is a parser-level setting or column-level
  - How to handle quoted fields in delimited formats
  - Whether to leverage Python's `csv` module or parse manually for consistency with the fixed-width approach
- **Open questions**:
  - How common are delimited formats in the inewave file ecosystem vs. fixed-width?
  - Should multi-character delimiters be supported?

## Dependencies

- **Blocked By**: ticket-021
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
