# ticket-014 Migrate FloatField Benchmark to pytest-benchmark

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Replace the manual timeit-based benchmark in `benchmarks/bench_floatfield_write.py` with pytest-benchmark tests using the `@pytest.mark.benchmark` marker. The new benchmark tests should cover the same 6 scenarios (F fits, F precision reduction, F rounding carry, E non-zero, D non-zero, E/D zero) but use `benchmark.pedantic()` for statistical rigor. The existing smoke test in `test_floatfield.py` should be updated to reference the new benchmark infrastructure.

## Anticipated Scope

- **Files likely to be modified**: `tests/components/test_floatfield_benchmark.py` (create), `benchmarks/bench_floatfield_write.py` (preserve as reference or remove), `tests/components/test_floatfield.py` (update or remove `test_floatfield_benchmark_smoke`)
- **Key decisions needed**: Whether to keep the old benchmark file alongside the new one or remove it, what `rounds`/`iterations` parameters to use for pytest-benchmark, whether to benchmark additional field types beyond FloatField
- **Open questions**: Should we benchmark `_textual_write()` directly or the full `write()` method? What warmup strategy to use? Should benchmark results be compared against a baseline?

## Dependencies

- **Blocked By**: ticket-006-add-py-typed-and-dev-deps (pytest-benchmark must be installed), ticket-002-add-pytest-configuration (benchmark marker must be registered), ticket-009-create-benchmark-workflow (CI workflow for running benchmarks)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
