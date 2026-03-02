# ticket-014 Migrate FloatField Benchmark to pytest-benchmark

## Context

### Background

The cfinterface project has a manual benchmark at `benchmarks/bench_floatfield_write.py` that uses `timeit.repeat()` to measure `FloatField._textual_write()` performance across 6 scenarios (F fits at full precision, F precision reduction, F rounding carry, E non-zero, D non-zero, E/D zero). It runs 100,000 writes per scenario with 5 repeats and prints a text table to stdout. The test file `tests/components/test_floatfield.py` has a smoke test (`test_floatfield_benchmark_smoke`, lines 201-212) that imports from the benchmark module and runs a tiny subset to verify it does not crash.

Epic 01 added `pytest-benchmark` as a dev dependency and registered the `benchmark` marker in `pyproject.toml`. Epic 02 created `.github/workflows/benchmark.yml` that runs `pytest -m benchmark --benchmark-only` with configurable `--benchmark-min-rounds`. The CI infrastructure is ready but no pytest-benchmark tests exist yet.

### Relation to Epic

This is the fourth and final ticket in Epic 03. It replaces the manual timeit-based benchmark with pytest-benchmark tests that integrate into the CI workflow created in ticket-009 and use the `benchmark` marker registered in ticket-002.

### Current State

- `benchmarks/bench_floatfield_write.py` exists with 82 lines: defines `_make_fields()`, `_bench_scenario()`, `run_benchmarks()`, and a `__main__` guard. It uses `timeit.repeat()` with no statistical analysis.
- `tests/components/test_floatfield.py` lines 201-212 contain `test_floatfield_benchmark_smoke()` which imports `_bench_scenario` and `_make_fields` from the benchmark module and runs a tiny (100 writes, 1 repeat) sanity check.
- `pyproject.toml` markers: `"benchmark: performance benchmarks (deselect with -m 'not benchmark')"`.
- `.github/workflows/benchmark.yml` runs `pytest -m benchmark --benchmark-only --benchmark-min-rounds=${{ inputs.benchmark-min-rounds }}`.
- `pytest-benchmark` is in `[project.optional-dependencies] dev`.

## Specification

### Requirements

1. Create `tests/components/test_floatfield_benchmark.py` with pytest-benchmark tests for all 6 scenarios from the original benchmark:
   - "F fits at full precision": `FloatField(12, 0, 4, format="F")` with values `[i + 0.1234 for i in range(100)]`
   - "F precision reduction": `FloatField(8, 0, 4, format="F")` with values `[12345.6789 + i for i in range(100)]`
   - "F rounding carry": `FloatField(5, 0, 2, format="F")` with values `[999.99 + i * 1000 for i in range(100)]`
   - "E non-zero": `FloatField(12, 0, 4, format="E")` with values `[i + 0.1234 for i in range(1, 101)]`
   - "D non-zero": `FloatField(12, 0, 4, format="D")` with values `[i + 0.1234 for i in range(1, 101)]`
   - "E/D zero": `FloatField(12, 0, 4, format="E")` with zero values + `FloatField(12, 0, 4, format="D")` with zero values

2. Each test function must:
   - Be decorated with `@pytest.mark.benchmark`.
   - Accept the `benchmark` fixture provided by pytest-benchmark.
   - Use `benchmark.pedantic(target, rounds=10, iterations=100)` for statistical rigor.
   - The target function calls `_textual_write()` on all fields in the scenario once per iteration.

3. Remove the smoke test `test_floatfield_benchmark_smoke` from `tests/components/test_floatfield.py` (lines 201-212) since it only existed to validate the old benchmark infrastructure. The pytest-benchmark tests fully replace its purpose.

4. Preserve `benchmarks/bench_floatfield_write.py` as a standalone CLI tool. Do NOT delete it. It serves as a quick local comparison tool that does not require pytest.

### Inputs/Props

- The `benchmark` fixture is injected by `pytest-benchmark` automatically.

### Outputs/Behavior

- `tests/components/test_floatfield_benchmark.py` with 6 test functions, one per scenario.
- `tests/components/test_floatfield.py` modified to remove lines 201-212 (`test_floatfield_benchmark_smoke` and its imports).

### Error Handling

- No special error handling needed. Benchmarks measure performance; they do not assert correctness (that is covered by existing unit tests and hypothesis tests).

## Acceptance Criteria

- [ ] Given the file `tests/components/test_floatfield_benchmark.py` is created, when `pytest tests/components/test_floatfield_benchmark.py -m benchmark --benchmark-only -v` is executed, then all 6 benchmark tests run and produce timing statistics in the pytest-benchmark output table.
- [ ] Given `pytest tests/ -m "not benchmark"` is executed, when the benchmark tests are deselected, then all remaining tests (including the full existing suite minus the removed smoke test) pass with exit code 0.
- [ ] Given `test_floatfield_benchmark_smoke` existed in `tests/components/test_floatfield.py`, when ticket-014 is complete, then that function and its associated imports (lines 201-212) no longer exist in the file.
- [ ] Given `benchmarks/bench_floatfield_write.py` exists before this ticket, when ticket-014 is complete, then the file still exists unchanged and `python benchmarks/bench_floatfield_write.py` runs without error.
- [ ] Given `ruff check tests/components/test_floatfield_benchmark.py tests/components/test_floatfield.py` is executed, then zero violations are reported.

## Implementation Guide

### Suggested Approach

1. Create `tests/components/test_floatfield_benchmark.py`:

   ```python
   """pytest-benchmark tests for FloatField._textual_write() performance."""

   import pytest
   from cfinterface.components.floatfield import FloatField


   def _make_fields(size, dec, fmt, values):
       return [FloatField(size, 0, dec, format=fmt, value=v) for v in values]


   def _write_all(fields):
       for f in fields:
           f._textual_write()


   @pytest.mark.benchmark
   def test_bench_f_fits_full_precision(benchmark):
       fields = _make_fields(12, 4, "F", [float(i) + 0.1234 for i in range(100)])
       benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


   @pytest.mark.benchmark
   def test_bench_f_precision_reduction(benchmark):
       fields = _make_fields(8, 4, "F", [12345.6789 + i for i in range(100)])
       benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


   @pytest.mark.benchmark
   def test_bench_f_rounding_carry(benchmark):
       fields = _make_fields(5, 2, "F", [999.99 + i * 1000 for i in range(100)])
       benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


   @pytest.mark.benchmark
   def test_bench_e_non_zero(benchmark):
       fields = _make_fields(12, 4, "E", [float(i) + 0.1234 for i in range(1, 101)])
       benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


   @pytest.mark.benchmark
   def test_bench_d_non_zero(benchmark):
       fields = _make_fields(12, 4, "D", [float(i) + 0.1234 for i in range(1, 101)])
       benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


   @pytest.mark.benchmark
   def test_bench_ed_zero(benchmark):
       fields = (
           _make_fields(12, 4, "E", [0.0] * 50)
           + _make_fields(12, 4, "D", [0.0] * 50)
       )
       benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)
   ```

2. Edit `tests/components/test_floatfield.py` to remove the smoke test:
   - Remove `test_floatfield_benchmark_smoke` function (lines 201-212).
   - Remove the `import sys` and `import os` inside it (they are local imports, so no top-level change needed).

3. Verify:
   - `pytest tests/components/test_floatfield_benchmark.py -m benchmark --benchmark-only -v` passes.
   - `pytest tests/ -m "not benchmark"` passes with all non-benchmark tests green.
   - `python benchmarks/bench_floatfield_write.py` still runs.
   - `ruff check tests/components/test_floatfield_benchmark.py tests/components/test_floatfield.py` passes.

### Key Files to Modify

- `tests/components/test_floatfield_benchmark.py` (CREATE)
- `tests/components/test_floatfield.py` (MODIFY -- remove lines 201-212)

### Patterns to Follow

- Reuse the same `_make_fields()` helper pattern from the original `benchmarks/bench_floatfield_write.py`.
- Use `benchmark.pedantic()` instead of `benchmark()` for explicit control over rounds and iterations.
- Use `@pytest.mark.benchmark` matching the marker registered in `pyproject.toml`.
- Benchmark `_textual_write()` directly (not `write()`), matching what the original benchmark measures.

### Pitfalls to Avoid

- Do NOT delete `benchmarks/bench_floatfield_write.py` -- it serves as a standalone CLI tool.
- Do NOT use `benchmark()` (the simple form) -- use `benchmark.pedantic()` for deterministic round/iteration counts that produce stable CI results.
- Do NOT add assertions inside benchmark functions -- they are for performance measurement, not correctness testing.
- Do NOT forget to remove the smoke test from `test_floatfield.py` -- it imports from `benchmarks/` using `sys.path` manipulation, which is fragile and no longer needed.
- Ensure the `--benchmark-disable` flag (used by default in normal test runs) does not cause benchmark tests to error out. With `@pytest.mark.benchmark` and `pytest -m "not benchmark"`, they are simply deselected.

## Testing Requirements

### Unit Tests

Not applicable -- benchmarks measure performance, not correctness. Correctness is covered by `test_floatfield.py` and `test_field_hypothesis.py`.

### Integration Tests

Verify that `pytest -m benchmark --benchmark-only` collects and runs all 6 benchmark tests, matching what `.github/workflows/benchmark.yml` expects.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-006-add-py-typed-and-dev-deps.md (pytest-benchmark must be installed), ticket-002-add-pytest-configuration.md (benchmark marker must be registered), ticket-009-create-benchmark-workflow.md (CI workflow expects pytest-benchmark tests)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
