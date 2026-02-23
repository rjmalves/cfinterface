# ticket-022 Create TabularSection Convenience Base Class

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Create a `TabularSection` base class that extends `Section` and integrates with `TabularParser` to provide a declarative way to define sections that parse into DataFrames. Consumer subclasses only need to declare column specifications and optional header/footer patterns.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/components/tabular_section.py` (new), `cfinterface/components/__init__.py`, `tests/components/test_tabular_section.py` (new)
- **Key decisions needed**:
  - Whether column specs are class-level attributes or passed to `__init__`
  - How `read()` delegates to `TabularParser`
  - How `write()` converts DataFrame back to formatted lines
- **Open questions**:
  - Should `TabularSection.data` always be a DataFrame, or should it support dict-of-lists?
  - How to handle sections with variable numbers of header lines before the tabular data?
  - Should the section auto-detect the number of data rows (read until pattern/EOF)?

## Dependencies

- **Blocked By**: ticket-021
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
