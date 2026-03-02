# Epic 03: Test Infrastructure Enhancement

## Goal

Improve test robustness and developer experience with shared fixtures via conftest.py, pytest markers for categorization, hypothesis property-based testing for field round-trips, and pytest-benchmark integration replacing the manual timeit benchmark.

## Scope

- Create conftest.py with shared fixtures for common test patterns
- Add pytest markers (slow, benchmark) and register them
- Implement hypothesis strategies for FloatField, IntegerField, DatetimeField, LiteralField, and TabularParser round-trips
- Migrate benchmarks/bench_floatfield_write.py to pytest-benchmark
- Add property-based tests targeting parse/write round-trip correctness

## Out of Scope

- CI workflow changes (should already be done in Epic 2)
- Tool configuration (should already be done in Epic 1)
- Increasing coverage beyond current 94% (existing tests are sufficient; hypothesis may incidentally improve coverage)
- New feature tests (only infrastructure and property-based tests)

## Dependencies

- **Epic 1** must be completed (pytest markers registered in pyproject.toml, hypothesis/pytest-benchmark in dev deps)
- **Epic 2** should be completed (CI uses markers to skip benchmarks)

## Tickets

1. **ticket-011-create-conftest-and-fixtures** — Create conftest.py with shared test fixtures
2. **ticket-012-add-hypothesis-field-tests** — Add hypothesis property-based tests for field round-trips
3. **ticket-013-add-hypothesis-tabular-tests** — Add hypothesis property-based tests for TabularParser round-trips
4. **ticket-014-migrate-to-pytest-benchmark** — Replace manual timeit benchmark with pytest-benchmark

## Success Criteria

- conftest.py exists at tests/conftest.py with reusable fixtures
- Hypothesis tests exist for FloatField, IntegerField, DatetimeField, LiteralField, TabularParser
- pytest-benchmark tests exist and are skippable via `pytest -m "not benchmark"`
- All existing 392 tests still pass
- No pytest warnings about unknown markers
