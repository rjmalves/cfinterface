# Plan: Infrastructure & Documentation Overhaul

**Project**: cfinterface
**Plan**: infra-docs-overhaul
**Status**: In Progress (Progressive)
**Total Tickets**: 13 (11 detailed/refined, 2 outline)

## Overview

Modernize cfinterface's developer tooling, CI infrastructure, and documentation to match ecosystem standards. Adds pre-commit hooks, migrates GitHub Pages deployment, upgrades Sphinx to Furo theme, creates comprehensive pt-BR documentation content, and polishes the repository.

## Tech Stack

- Python (Sphinx, pre-commit)
- GitHub Actions (YAML workflows)
- reStructuredText (documentation)

## Epics

| Epic | Name                   | Tickets | Phase     |
| ---- | ---------------------- | ------- | --------- |
| 01   | CI & Developer Tooling | 3       | completed |
| 02   | Sphinx Modernization   | 3       | completed |
| 03   | Documentation Content  | 5       | executing |
| 04   | Repository Polish      | 2       | outline   |

## Dependency Graph

```
ticket-001 (pre-commit) ──────────────────────────────────> ticket-011 (contributing.rst)
ticket-002 (actions upgrade)                                     │
ticket-003 (docs deploy)                                         v
                                                            ticket-012 (CONTRIBUTING.md)
ticket-004 (Furo theme) ──> ticket-005 (examples)
         │
         └──> ticket-006 (conf.py language) ──> ticket-007 (architecture)
                                            ──> ticket-008 (FAQ)
                                            ──> ticket-009 (migration guide)
                                            ──> ticket-010 (performance tips)
                                                     │
                                                     v (all of 007-011)
                                               ticket-013 (index.rst)
```

## Progress Table

| Ticket     | Title                                                     | Epic    | Status    | Detail Level | Readiness | Quality | Badge     |
| ---------- | --------------------------------------------------------- | ------- | --------- | ------------ | --------- | ------- | --------- |
| ticket-001 | Add pre-commit configuration                              | epic-01 | completed | Detailed     | 0.97      | 0.95    | EXCELLENT |
| ticket-002 | Upgrade GitHub Actions versions                           | epic-01 | completed | Detailed     | 0.97      | 0.98    | EXCELLENT |
| ticket-003 | Migrate docs deployment to official GitHub Pages action   | epic-01 | completed | Detailed     | 0.97      | 0.98    | EXCELLENT |
| ticket-004 | Migrate Sphinx theme from RTD to Furo                     | epic-02 | completed | Detailed     | 0.97      | 0.98    | EXCELLENT |
| ticket-005 | Add sphinx-gallery examples for BlockFile and SectionFile | epic-02 | completed | Detailed     | 0.95      | 0.95    | EXCELLENT |
| ticket-006 | Update conf.py language and intersphinx settings          | epic-02 | completed | Detailed     | 0.97      | 0.98    | EXCELLENT |
| ticket-007 | Create architecture overview page                         | epic-03 | completed | Refined      | 1.00      | 0.95    | EXCELLENT |
| ticket-008 | Create FAQ page                                           | epic-03 | completed | Refined      | 1.00      | 0.95    | EXCELLENT |
| ticket-009 | Create v1.8-to-v1.9 migration guide                       | epic-03 | completed | Refined      | 1.00      | 0.95    | EXCELLENT |
| ticket-010 | Create performance tips page                              | epic-03 | completed | Refined      | 1.00      | 0.95    | EXCELLENT |
| ticket-011 | Update contributing.rst content and fix repository URL    | epic-03 | completed | Refined      | 0.98      | 0.95    | EXCELLENT |
| ticket-012 | Create root-level CONTRIBUTING.md                         | epic-04 | pending   | Outline      | --        | --      | --        |
| ticket-013 | Restructure index.rst with new documentation sections     | epic-04 | pending   | Outline      | --        | --      | --        |

## Readiness Scores (Detailed/Refined Tickets)

| Ticket     | Composite | Structure | Testability | Boundary | Dep Clarity | Atomicity |
| ---------- | --------- | --------- | ----------- | -------- | ----------- | --------- |
| ticket-001 | 0.97      | 1.00      | 0.95        | 0.95     | 1.00        | 1.00      |
| ticket-002 | 0.97      | 1.00      | 1.00        | 0.95     | 1.00        | 0.90      |
| ticket-003 | 0.97      | 1.00      | 1.00        | 1.00     | 1.00        | 0.90      |
| ticket-004 | 0.97      | 1.00      | 1.00        | 1.00     | 1.00        | 0.90      |
| ticket-005 | 0.95      | 1.00      | 0.90        | 0.95     | 1.00        | 0.90      |
| ticket-006 | 0.97      | 1.00      | 1.00        | 0.90     | 1.00        | 1.00      |
| ticket-007 | 1.00      | 1.00      | 1.00        | 1.00     | 1.00        | 1.00      |
| ticket-008 | 1.00      | 1.00      | 1.00        | 1.00     | 1.00        | 1.00      |
| ticket-009 | 1.00      | 1.00      | 1.00        | 1.00     | 1.00        | 1.00      |
| ticket-010 | 1.00      | 1.00      | 1.00        | 1.00     | 1.00        | 1.00      |
| ticket-011 | 0.98      | 1.00      | 1.00        | 1.00     | 1.00        | 0.80      |

Dimensions below 0.85: ticket-011:atomicity (0.80 -- title contains "and", preserved from original outline)
