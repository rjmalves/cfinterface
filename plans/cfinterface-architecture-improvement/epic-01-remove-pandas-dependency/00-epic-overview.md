# Epic 01: Remove pandas Dependency from Core

## Overview

Remove the runtime dependency on pandas from cfinterface's core modules. Currently, all four Field subclasses (FloatField, IntegerField, LiteralField, DatetimeField) import pandas at module level solely for `pd.isnull()` null checking. Additionally, `RegisterFile._as_df()` uses `pd.DataFrame` for a convenience conversion method.

This epic replaces `pd.isnull()` with a native null-checking utility function and moves pandas to an optional dependency. The `_as_df()` method is preserved but uses a lazy import.

## Goals

1. Eliminate `import pandas as pd` from all four Field subclass modules
2. Create a lightweight `_is_null()` utility that handles `None`, `float('nan')`, and `numpy.nan`
3. Move pandas from `dependencies` to `[project.optional-dependencies]` in pyproject.toml
4. Convert `RegisterFile._as_df()` to use lazy pandas import with a clear error message if pandas is not installed
5. Ensure all existing tests pass

## Scope

### In Scope

- cfinterface/components/floatfield.py
- cfinterface/components/integerfield.py
- cfinterface/components/literalfield.py
- cfinterface/components/datetimefield.py
- cfinterface/files/registerfile.py
- cfinterface/\_utils/**init**.py (new utility function)
- pyproject.toml

### Out of Scope

- Changes to inewave or sintetizador-newave
- Changes to data containers or adapters
- Any API changes visible to consumers

## Tickets

| Ticket     | Title                                                | Effort |
| ---------- | ---------------------------------------------------- | ------ |
| ticket-001 | Create native null-checking utility function         | 1      |
| ticket-002 | Replace pd.isnull() in all Field subclasses          | 2      |
| ticket-003 | Convert RegisterFile.\_as_df() to lazy pandas import | 1      |
| ticket-004 | Move pandas to optional dependency in pyproject.toml | 1      |

## Success Criteria

- `import cfinterface` succeeds without pandas installed
- All existing tests pass (with pandas installed for test environment)
- New tests verify \_is_null() handles None, float('nan'), numpy.nan, and normal values
- `RegisterFile._as_df()` raises ImportError with helpful message when pandas is not installed
