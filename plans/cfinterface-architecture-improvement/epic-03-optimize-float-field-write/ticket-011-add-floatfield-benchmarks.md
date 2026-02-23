# ticket-011 Add FloatField Write Benchmark Tests

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Create a benchmark test suite using pytest-benchmark that measures `FloatField._textual_write()` performance across different format types (F, E, D), field sizes, and value ranges. This provides quantitative evidence of the improvement from ticket-010 and a regression baseline for future changes.

## Anticipated Scope

- **Files likely to be modified**: `tests/benchmarks/` (new directory), `pyproject.toml` (add pytest-benchmark to dev deps)
- **Key decisions needed**: Whether to use pytest-benchmark or a simpler time-based approach; benchmark parameters (number of iterations, field sizes, value ranges)
- **Open questions**:
  - Should benchmarks be in a separate directory or alongside existing tests?
  - What is the baseline performance of the current loop-based approach?
  - Should binary write also be benchmarked?

## Dependencies

- **Blocked By**: ticket-010
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: Low (will be re-estimated during refinement)
