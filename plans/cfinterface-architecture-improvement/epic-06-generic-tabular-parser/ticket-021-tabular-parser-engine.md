# ticket-021 Implement TabularParser Core Engine

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Create a `TabularParser` class in a new `cfinterface/parsers/` module that accepts a list of column specifications (field type, size, starting position, column name) and transforms a sequence of text lines into a pandas DataFrame. This is the core engine that consumer packages will use to replace per-file custom parsing.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/parsers/__init__.py` (new), `cfinterface/parsers/tabular.py` (new), `tests/parsers/test_tabular.py` (new)
- **Key decisions needed**:
  - Column specification format: list of tuples, dataclass, or a `ColumnDef` named tuple
  - Whether to produce a pandas DataFrame or a dict-of-lists (with optional pandas conversion)
  - How to handle the pandas optional dependency (lazy import like RegisterFile.\_as_df())
- **Open questions**:
  - Should the parser accept raw strings or File IO objects?
  - Should it handle header detection/skipping?
  - How should parse errors (malformed rows) be handled -- skip, raise, or fill with NaN?

## Dependencies

- **Blocked By**: ticket-002 (needs \_is_null utility), ticket-017 (needs typed field patterns)
- **Blocks**: ticket-022, ticket-023

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
