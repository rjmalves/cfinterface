# cfinterface Quality, CI/CD, and Documentation Overhaul

Post-architecture-overhaul quality plan for cfinterface v1.9.0.

## Tech Stack

- Python 3.10+ (numpy>=2.0.0)
- pytest / pytest-cov / pytest-benchmark / hypothesis
- mypy / ty / ruff
- Sphinx (RTD theme, autodoc, numpydoc)
- GitHub Actions CI/CD

## Epic Summary

| Epic | Name                            | Tickets | Detail Level | Phase     |
| ---- | ------------------------------- | ------- | ------------ | --------- |
| 01   | pyproject.toml and Tool Config  | 6       | Detailed     | Executing |
| 02   | CI/CD Pipeline Overhaul         | 4       | Detailed     | Executing |
| 03   | Test Infrastructure Enhancement | 4       | Outline      | Outline   |
| 04   | Sphinx Documentation            | 4       | Outline      | Outline   |
| 05   | CHANGELOG and Release Prep      | 2       | Outline      | Outline   |

**Total**: 20 tickets (10 detailed, 10 outline)

## Dependency Graph

```
ticket-001 (classifiers) ──────────────────────────────┐
ticket-002 (pytest config) ──┬── ticket-007 (matrix) ──┤
ticket-003 (mypy config) ────┤                          │
                              └── ticket-004 (mypy fix)─┼── ticket-008 (lint job)
ticket-005 (coverage/ruff) ─────────────────────────────┘
ticket-006 (py.typed/deps) ─┬── ticket-009 (benchmark wf)
                             │
ticket-007 (matrix) ────────┬── ticket-008 (lint job) ──┬── ticket-010 (docs/publish wf)
                             │                           │
ticket-011 (conftest) ──────┼── ticket-012 (hypothesis fields)
                             ├── ticket-013 (hypothesis tabular)
                             └── ticket-014 (benchmark migration)
ticket-015 (tabular docs) ──┐
ticket-016 (versioning docs)┼── ticket-018 (docstrings/index)
ticket-017 (storage docs) ──┘
ticket-019 (changelog) ──────── ticket-020 (release review)
```

## Progress Tracking

| Ticket     | Title                                                      | Epic    | Status    | Detail Level | Readiness | Quality | Badge |
| ---------- | ---------------------------------------------------------- | ------- | --------- | ------------ | --------- | ------- | ----- |
| ticket-001 | Update Python Classifiers and Project Metadata             | epic-01 | completed | Detailed     | 1.00      | --      | --    |
| ticket-002 | Add pytest Configuration to pyproject.toml                 | epic-01 | completed | Detailed     | 1.00      | --      | --    |
| ticket-003 | Add mypy Configuration to pyproject.toml                   | epic-01 | completed | Detailed     | 1.00      | --      | --    |
| ticket-004 | Fix mypy Strict Type Annotation Errors                     | epic-01 | completed | Detailed     | 0.92      | --      | --    |
| ticket-005 | Add Coverage and Expanded Ruff Configuration               | epic-01 | completed | Detailed     | 0.96      | --      | --    |
| ticket-006 | Add py.typed Marker and New Dev Dependencies               | epic-01 | completed | Detailed     | 1.00      | --      | --    |
| ticket-007 | Expand CI Test Matrix to Python 3.10-3.14 and Windows      | epic-02 | pending   | Detailed     | 1.00      | --      | --    |
| ticket-008 | Extract Lint/Quality Job with ty Evaluation                | epic-02 | pending   | Detailed     | 0.97      | --      | --    |
| ticket-009 | Create Manual-Dispatch Benchmark Workflow                  | epic-02 | pending   | Detailed     | 1.00      | --      | --    |
| ticket-010 | Update Docs and Publish Workflows                          | epic-02 | pending   | Detailed     | 1.00      | --      | --    |
| ticket-011 | Create conftest.py with Shared Test Fixtures               | epic-03 | pending   | Outline      | --        | --      | --    |
| ticket-012 | Add Hypothesis Property-Based Tests for Field Round-Trips  | epic-03 | pending   | Outline      | --        | --      | --    |
| ticket-013 | Add Hypothesis Property-Based Tests for TabularParser      | epic-03 | pending   | Outline      | --        | --      | --    |
| ticket-014 | Migrate FloatField Benchmark to pytest-benchmark           | epic-03 | pending   | Outline      | --        | --      | --    |
| ticket-015 | Create Sphinx Reference Pages for TabularParser            | epic-04 | pending   | Outline      | --        | --      | --    |
| ticket-016 | Create Sphinx Reference Page for Versioning Module         | epic-04 | pending   | Outline      | --        | --      | --    |
| ticket-017 | Create Sphinx Reference Pages for StorageType and Adapters | epic-04 | pending   | Outline      | --        | --      | --    |
| ticket-018 | Fix Missing Docstrings and Update Documentation Index      | epic-04 | pending   | Outline      | --        | --      | --    |
| ticket-019 | Create CHANGELOG.md for v1.9.0                             | epic-05 | pending   | Outline      | --        | --      | --    |
| ticket-020 | Final Release Preparation Review                           | epic-05 | pending   | Outline      | --        | --      | --    |
