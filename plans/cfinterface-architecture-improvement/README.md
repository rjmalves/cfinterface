# cfinterface Architecture and Performance Improvement

## Overview

Comprehensive architectural and performance improvement for the cfinterface Python package -- a file schema modeling framework used to parse/write dozens of legacy HPC file formats. Changes are ordered by impact and risk, starting with foundational improvements and progressing to consumer-facing features.

## Tech Stack

- Python >=3.10, numpy >=2.0.0
- pandas >=2.2.3 (moved to optional dependency in Epic 01)
- pytest, ruff, mypy (dev tools)

## Epics

| Epic | Name                             | Tickets | Detail Level | Phase     |
| ---- | -------------------------------- | ------- | ------------ | --------- |
| 01   | Remove pandas dependency         | 4       | Detailed     | Completed |
| 02   | Compile regex + StorageType enum | 5       | Detailed     | Completed |
| 03   | Optimize FloatField write        | 2       | Refined      | Completed |
| 04   | Array-backed data containers     | 5       | Refined      | Completed |
| 05   | Type-safe text/binary dispatch   | 4       | Refined      | Completed |
| 06   | Generic tabular parser           | 3       | Refined      | Completed |
| 07   | Schema versioning + batch ops    | 4       | Outline      | Outline   |

## Progress

| Ticket     | Title                                                           | Epic    | Status    | Detail Level |
| ---------- | --------------------------------------------------------------- | ------- | --------- | ------------ |
| ticket-001 | Create native null-checking utility function                    | epic-01 | completed | Detailed     |
| ticket-002 | Replace pd.isnull() in all Field subclasses                     | epic-01 | completed | Detailed     |
| ticket-003 | Convert RegisterFile.\_as_df() to lazy pandas import            | epic-01 | completed | Detailed     |
| ticket-004 | Move pandas to optional dependency in pyproject.toml            | epic-01 | completed | Detailed     |
| ticket-005 | Add regex pattern compilation and caching                       | epic-02 | completed | Detailed     |
| ticket-006 | Create StorageType enum module                                  | epic-02 | completed | Detailed     |
| ticket-007 | Update all factory functions to accept StorageType              | epic-02 | completed | Detailed     |
| ticket-008 | Migrate internal storage parameter usage to StorageType         | epic-02 | completed | Detailed     |
| ticket-009 | Add deprecation warnings for string-based storage               | epic-02 | completed | Detailed     |
| ticket-010 | Optimize FloatField fixed-point textual write                   | epic-03 | completed | Refined      |
| ticket-011 | Add FloatField write benchmark tests                            | epic-03 | completed | Refined      |
| ticket-012 | Implement list-backed RegisterData container                    | epic-04 | completed | Refined      |
| ticket-013 | Implement list-backed BlockData container                       | epic-04 | completed | Refined      |
| ticket-014 | Implement list-backed SectionData container                     | epic-04 | completed | Refined      |
| ticket-015 | Migrate Register/Block/Section prev/next to computed properties | epic-04 | completed | Refined      |
| ticket-016 | Add type-indexed lookup optimization                            | epic-04 | completed | Refined      |
| ticket-017 | Design typed Field read/write protocol                          | epic-05 | completed | Refined      |
| ticket-018 | Separate TextualRepository and BinaryRepository type signatures | epic-05 | completed | Refined      |
| ticket-019 | Update Line class for typed dispatch                            | epic-05 | completed | Refined      |
| ticket-020 | Update Register/Block/Section for typed IO paths                | epic-05 | completed | Refined      |
| ticket-021 | Implement TabularParser core engine                             | epic-06 | completed | Refined      |
| ticket-022 | Create TabularSection convenience base class                    | epic-06 | completed | Refined      |
| ticket-023 | Add delimited tabular parsing support                           | epic-06 | completed | Refined      |
| ticket-024 | Design SchemaVersion descriptor and registry                    | epic-07 | pending   | Outline      |
| ticket-025 | Implement instance-level version binding                        | epic-07 | pending   | Outline      |
| ticket-026 | Add batch read_many() API to file classes                       | epic-07 | pending   | Outline      |
| ticket-027 | Add version validation and mismatch detection                   | epic-07 | pending   | Outline      |
