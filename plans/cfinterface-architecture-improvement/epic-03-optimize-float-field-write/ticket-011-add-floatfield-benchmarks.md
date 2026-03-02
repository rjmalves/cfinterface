# ticket-011 Add FloatField Write Benchmark Tests

## Context

### Background

Ticket-010 replaces the O(decimal_digits) precision-reduction loop in `FloatField._textual_write()` with a direct-computation approach that uses at most 3 format calls. To provide quantitative evidence of the improvement and establish a regression baseline for future changes, a benchmark test suite is needed.

Preliminary profiling (during refinement analysis) showed:

- **F format, value fits at full precision**: ~0.92 us/write (current) -- the most common case, enters the loop but breaks on the first iteration
- **F format, value requires precision reduction**: ~2.30 us/write (current) -- loop iterates multiple times
- The optimization is expected to yield a 1.3-1.8x speedup depending on how often precision reduction is needed.

The project does not currently have any benchmark infrastructure. This ticket introduces a lightweight, standalone benchmark script using Python's `timeit` module rather than adding a new dev dependency (`pytest-benchmark`). This keeps the dev dependency set stable and avoids CI complexity.

### Relation to Epic

This is the second and final ticket of Epic 03 (Optimize FloatField Write). It validates the performance improvement from ticket-010 and provides a benchmark script that can be rerun manually to detect regressions in future epics.

### Current State

- `tests/components/test_floatfield.py` contains 17+ functional tests (read, write, binary, NaN, scientific notation) plus new correctness tests from ticket-010. No performance tests exist.
- `pyproject.toml` dev dependencies: `pytest`, `pytest-cov`, `ruff`, `mypy`, `sphinx-rtd-theme`, `sphinx-gallery`, `sphinx`, `numpydoc`, `plotly`, `matplotlib`. No `pytest-benchmark`.
- There is no `benchmarks/` directory in the project.

## Specification

### Requirements

1. Create a new file `benchmarks/bench_floatfield_write.py` containing benchmark functions for `FloatField._textual_write()` across different scenarios.
2. The benchmark script must be a standalone Python script runnable with `python benchmarks/bench_floatfield_write.py` -- no new dependencies required.
3. Use Python's `timeit` module for timing, with configurable iteration counts.
4. Cover the following scenarios:
   - **F format, value fits at full precision** (no precision reduction needed)
   - **F format, value requires precision reduction** (loop-equivalent path)
   - **F format, rounding carry edge case** (third format attempt triggered)
   - **E format, non-zero value** (direct format + truncation path, not in the else branch)
   - **D format, non-zero value** (direct format + truncation + replace path)
   - **E/D format, value == 0** (else branch for scientific notation zero)
5. Report results as microseconds per write operation, with min/mean/max across runs.
6. Add a pytest-based smoke test in `tests/components/test_floatfield.py` that verifies the benchmark script can be imported and its core benchmark function executes without error (not a performance assertion, just a sanity check).

### Inputs/Props

The benchmark script takes no command-line arguments by default. Iteration counts and scenario parameters are defined as constants at the top of the script for easy modification.

### Outputs/Behavior

When run, the script prints a formatted table to stdout:

```
FloatField._textual_write() Benchmark
======================================
Scenario                        | N writes |  min (us) |  mean (us) |  max (us)
F fits at full precision        |   100000 |      0.XX |       0.XX |      0.XX
F requires precision reduction  |   100000 |      0.XX |       0.XX |      0.XX
F rounding carry                |   100000 |      0.XX |       0.XX |      0.XX
E non-zero                      |   100000 |      0.XX |       0.XX |      0.XX
D non-zero                      |   100000 |      0.XX |       0.XX |      0.XX
E/D zero                        |   100000 |      0.XX |       0.XX |      0.XX
```

### Error Handling

If the `cfinterface` package cannot be imported, the script prints a clear error message and exits with code 1. No other error conditions are expected.

## Acceptance Criteria

- [ ] Given the file `benchmarks/bench_floatfield_write.py` exists, when `python benchmarks/bench_floatfield_write.py` is executed from the repository root, then it runs to completion and prints a formatted table with timing results for all 6 scenarios
- [ ] Given each benchmark scenario, when it is run, then it exercises at least 100,000 write operations and reports min/mean/max microseconds per write
- [ ] Given the benchmark script, when it is imported as a module (`from benchmarks.bench_floatfield_write import run_benchmarks`), then `run_benchmarks()` executes without error
- [ ] Given the test file `tests/components/test_floatfield.py`, when `pytest tests/components/test_floatfield.py` is run, then a smoke test for the benchmark script passes
- [ ] Given the benchmark results, when compared to the pre-optimization baseline (if available via git stash or branch comparison), then the F-format precision-reduction scenario shows measurable improvement (this is a manual verification step, not an automated assertion)
- [ ] No new entries are added to `pyproject.toml` dependencies or optional-dependencies

## Implementation Guide

### Suggested Approach

1. Create the `benchmarks/` directory at the repository root.
2. Create `benchmarks/__init__.py` (empty, to make it importable for the smoke test).
3. Create `benchmarks/bench_floatfield_write.py` with the following structure:

```python
"""Benchmark FloatField._textual_write() across format types and scenarios."""

import timeit
from cfinterface.components.floatfield import FloatField


# --- Configuration ---
N_WRITES = 100_000
N_REPEATS = 5  # number of timeit repeats to get min/mean/max


def _make_fields(size, dec, fmt, values):
    """Create a list of FloatField instances with given parameters."""
    return [FloatField(size, 0, dec, format=fmt, value=v) for v in values]


def _bench_scenario(name, fields, n_writes, n_repeats):
    """Run a single benchmark scenario and return (name, n, min, mean, max)."""
    n_fields = len(fields)
    loops = n_writes // n_fields

    def run():
        for _ in range(loops):
            for f in fields:
                f._textual_write()

    times = timeit.repeat(run, number=1, repeat=n_repeats)
    per_write = [t / n_writes * 1e6 for t in times]  # microseconds
    return name, n_writes, min(per_write), sum(per_write) / len(per_write), max(per_write)


def run_benchmarks():
    """Run all benchmark scenarios and print results."""
    scenarios = [
        (
            "F fits at full precision",
            _make_fields(12, 4, "F", [float(i) + 0.1234 for i in range(100)]),
        ),
        (
            "F requires precision reduction",
            _make_fields(8, 4, "F", [12345.6789 + i for i in range(100)]),
        ),
        (
            "F rounding carry",
            _make_fields(5, 2, "F", [999.99 + i * 1000 for i in range(100)]),
        ),
        (
            "E non-zero",
            _make_fields(12, 4, "E", [float(i) + 0.1234 for i in range(1, 101)]),
        ),
        (
            "D non-zero",
            _make_fields(12, 4, "D", [float(i) + 0.1234 for i in range(1, 101)]),
        ),
        (
            "E/D zero",
            _make_fields(12, 4, "E", [0.0] * 50)
            + _make_fields(12, 4, "D", [0.0] * 50),
        ),
    ]

    header = f"{'Scenario':<35} | {'N writes':>8} | {'min (us)':>9} | {'mean (us)':>10} | {'max (us)':>9}"
    print("FloatField._textual_write() Benchmark")
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    for name, fields in scenarios:
        result = _bench_scenario(name, fields, N_WRITES, N_REPEATS)
        print(
            f"{result[0]:<35} | {result[1]:>8} | {result[2]:>9.2f} | {result[3]:>10.2f} | {result[4]:>9.2f}"
        )


if __name__ == "__main__":
    run_benchmarks()
```

4. Add a smoke test to `tests/components/test_floatfield.py`:

```python
def test_floatfield_benchmark_smoke():
    """Verify the benchmark script can run without errors."""
    import sys
    import os
    # Ensure benchmarks dir is importable
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from benchmarks.bench_floatfield_write import _bench_scenario, _make_fields

    fields = _make_fields(12, 4, "F", [1.234, 5.678])
    name, n, mn, mean, mx = _bench_scenario("smoke", fields, 100, 1)
    assert name == "smoke"
    assert n == 100
    assert mn > 0
```

### Key Files to Modify

- `benchmarks/__init__.py` -- new empty file (makes the directory importable)
- `benchmarks/bench_floatfield_write.py` -- new benchmark script
- `tests/components/test_floatfield.py` -- add smoke test function at end of file

### Patterns to Follow

- Append new tests to the existing test file, do not create a separate test file (epic-02 learnings).
- Use standalone script approach (no new dev dependency) consistent with the project's minimal-dependency philosophy.
- Follow `ruff` formatting with 80-character line length (from `pyproject.toml`).

### Pitfalls to Avoid

1. **Do NOT add `pytest-benchmark` to `pyproject.toml`.** The project has a minimal dependency philosophy. Using `timeit` from stdlib is sufficient for this use case.
2. **Do NOT make performance assertions in the smoke test.** Benchmark times are not deterministic. The smoke test only verifies the benchmark code runs without error.
3. **Do NOT use `time.time()` or `time.perf_counter()` directly.** Use `timeit.repeat()` which handles setup overhead and GC correctly.
4. **Do NOT benchmark binary write.** The binary path (`_binary_write`) uses `numpy.tobytes()` and was not modified in ticket-010. Benchmarking it adds noise without measuring the optimization.

## Testing Requirements

### Unit Tests

Add one smoke test to `tests/components/test_floatfield.py` (described in Implementation Guide above). This test:

- Imports the benchmark functions from `benchmarks/bench_floatfield_write.py`
- Runs a single scenario with a small iteration count (100 writes)
- Asserts the function returns valid results (name matches, count matches, times are positive)
- Does NOT assert specific timing thresholds

### Integration Tests

No integration tests needed. The benchmark script is a standalone tool, not part of the application runtime.

## Dependencies

- **Blocked By**: ticket-010 (the optimization must be in place before benchmarking)
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: High
