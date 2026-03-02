# ticket-009 Create Manual-Dispatch Benchmark Workflow

## Context

### Background

cfinterface has one manual benchmark (`benchmarks/bench_floatfield_write.py`) using timeit. After Epic 3 migrates this to pytest-benchmark, there needs to be a CI workflow that can run benchmarks on demand. This workflow uses `workflow_dispatch` for manual triggering and runs pytest with the benchmark marker.

### Relation to Epic

Third ticket in Epic 2. Adds the benchmark CI workflow that complements the test and lint workflows. The actual pytest-benchmark tests are created in Epic 3 (ticket-014), but the workflow should be ready to receive them.

### Current State

- No benchmark workflow exists in `.github/workflows/`
- The existing `benchmarks/bench_floatfield_write.py` uses timeit (not pytest-benchmark)
- Pytest marker `benchmark` will be registered by ticket-002
- pytest-benchmark will be installed by ticket-006

## Specification

### Requirements

1. Create `.github/workflows/benchmark.yml` with `workflow_dispatch` trigger
2. The workflow should allow optional input for custom pytest arguments
3. Run on `ubuntu-latest` with Python 3.12
4. Execute: `uv run pytest -m benchmark --benchmark-only --benchmark-json=benchmark-results.json`
5. Upload the benchmark results JSON as a workflow artifact
6. Add a `benchmark-min-rounds` input with default value of 5 (for quick manual checks)

### Inputs/Props

- New file: `/home/rogerio/git/cfinterface/.github/workflows/benchmark.yml`

### Outputs/Behavior

Create `.github/workflows/benchmark.yml`:

```yaml
name: benchmarks

on:
  workflow_dispatch:
    inputs:
      benchmark-min-rounds:
        description: "Minimum rounds per benchmark"
        required: false
        default: "5"
        type: string

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Set up Python 3.12
        run: uv python install 3.12
      - name: Install the project
        run: |
          uv sync --all-extras --dev
      - name: Run benchmarks
        run: |
          uv run pytest -m benchmark --benchmark-only \
            --benchmark-min-rounds=${{ inputs.benchmark-min-rounds }} \
            --benchmark-json=benchmark-results.json
      - name: Upload benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark-results.json
          retention-days: 30
```

### Error Handling

- If no tests with the `benchmark` marker exist, pytest will report "no tests ran" and exit with code 5 (no tests collected). This is expected until Epic 3 ticket-014 creates benchmark tests.

## Acceptance Criteria

- [ ] Given the path `.github/workflows/benchmark.yml`, when checking file existence, then the file exists
- [ ] Given the file `.github/workflows/benchmark.yml`, when inspecting the `on` trigger, then it contains `workflow_dispatch` with a `benchmark-min-rounds` input
- [ ] Given the file `.github/workflows/benchmark.yml`, when inspecting the pytest command, then it includes `-m benchmark`, `--benchmark-only`, and `--benchmark-json`
- [ ] Given the file `.github/workflows/benchmark.yml`, when inspecting the artifact upload step, then it uploads `benchmark-results.json` with 30-day retention
- [ ] Given valid YAML, when parsing `.github/workflows/benchmark.yml` with a YAML parser, then no syntax errors are reported

## Implementation Guide

### Suggested Approach

1. Create `/home/rogerio/git/cfinterface/.github/workflows/benchmark.yml`
2. Write the workflow content as specified above
3. Validate YAML syntax

### Key Files to Modify

- `/home/rogerio/git/cfinterface/.github/workflows/benchmark.yml` (create)

### Patterns to Follow

- Mirror the uv/Python setup pattern from the other workflows
- Use `workflow_dispatch` with typed inputs for configurability
- Upload results as artifacts for historical tracking

### Pitfalls to Avoid

- Do NOT add `push` or `pull_request` triggers — benchmarks should only run on demand
- Do NOT use `--benchmark-disable` (that disables benchmarks; the opposite of what we want)
- Do NOT set `fail-fast` (single job, not a matrix)
- Ensure the `--benchmark-json` path is relative to the workspace root

## Testing Requirements

### Unit Tests

Not applicable — CI workflow creation.

### Integration Tests

- Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('.github/workflows/benchmark.yml'))"`

### E2E Tests

Not applicable — the workflow will report "no tests collected" until Epic 3 creates benchmark tests.

## Dependencies

- **Blocked By**: ticket-002-add-pytest-configuration (benchmark marker must be registered), ticket-006-add-py-typed-and-dev-deps (pytest-benchmark must be in dev deps)
- **Blocks**: ticket-014-migrate-to-pytest-benchmark (benchmark tests will use this workflow)

## Effort Estimate

**Points**: 1
**Confidence**: High
