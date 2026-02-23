# Epic 06: Generic Tabular Parser

## Overview

Many Section and Block subclasses in consumer packages like inewave parse tabular data (rows of fixed-width fields) into pandas DataFrames. Currently, each subclass reimplements this parsing logic from scratch: reading lines, splitting fields, building column lists, and constructing the DataFrame. This epic provides a reusable `TabularParser` component in cfinterface that standardizes this pattern.

## Goals

1. Create a `TabularParser` class that transforms a sequence of lines into a DataFrame given a column specification (field definitions + column names)
2. Provide a `TabularSection` convenience base class for Sections that produce tabular data
3. Support both fixed-width and delimited tabular formats
4. Reduce boilerplate in consumer Section/Block implementations by 60-80%

## Tickets

| Ticket     | Title                                        | Effort |
| ---------- | -------------------------------------------- | ------ |
| ticket-021 | Implement TabularParser core engine          | 3      |
| ticket-022 | Create TabularSection convenience base class | 2      |
| ticket-023 | Add delimited tabular parsing support        | 2      |

## Success Criteria

- A consumer can define a tabular Section in ~10 lines instead of ~50
- Existing patterns in inewave can be replaced by TabularSection subclasses
- All new components have comprehensive unit tests
- Parser handles edge cases: empty tables, partial rows, NaN values
