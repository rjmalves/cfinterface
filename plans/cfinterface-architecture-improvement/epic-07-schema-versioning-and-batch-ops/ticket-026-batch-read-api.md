# ticket-026 Add Batch read_many() API to File Classes

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Add a `read_many()` class method to `RegisterFile`, `BlockFile`, and `SectionFile` that reads multiple files with shared settings (version, encoding) in a single call, returning a list of file instances. This is the foundation for future parallel I/O and eliminates repeated per-file configuration in consumers like sintetizador-newave.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/files/registerfile.py`, `cfinterface/files/blockfile.py`, `cfinterface/files/sectionfile.py`
- **Key decisions needed**:
  - Whether `read_many()` accepts file paths or a directory glob pattern
  - Whether to use `concurrent.futures` for parallel I/O or keep it sequential initially
  - Error handling: fail-fast on first error, or collect all errors and report at the end
- **Open questions**:
  - What is the typical file count per batch in sintetizador-newave? (100+ nwlistop files)
  - Should `read_many()` support heterogeneous file types or only one type at a time?
  - Should the return type be a list or a dict keyed by file path?

## Dependencies

- **Blocked By**: ticket-025
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
