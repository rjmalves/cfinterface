# ticket-013 Add Hypothesis Property-Based Tests for TabularParser Round-Trips

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Implement hypothesis property-based tests that verify `TabularParser.parse_lines()` followed by `TabularParser.format_rows()` produces output that re-parses to equivalent data. This should cover both fixed-width and delimited parsing modes with varying column counts, field types, and data values. The property under test is: `parse(format(parse(lines))) == parse(lines)` for well-formed input.

## Anticipated Scope

- **Files likely to be modified**: `tests/components/test_tabular_hypothesis.py` (create), possibly `tests/conftest.py` (add TabularParser-specific strategies)
- **Key decisions needed**: How to generate valid input lines that respect field width constraints, whether to test TabularSection subclasses or just TabularParser directly, what column type combinations to test
- **Open questions**: How to handle the edge case where format_rows produces lines with different whitespace than the original (round-trip may not be byte-identical but semantically equivalent)? Should we test delimiter modes (semicolon, comma, tab) as separate hypothesis tests or parametrize?

## Dependencies

- **Blocked By**: ticket-006-add-py-typed-and-dev-deps (hypothesis must be installed), ticket-011-create-conftest-and-fixtures (shared fixtures/strategies), ticket-012-add-hypothesis-field-tests (field strategies may be reused)
- **Blocks**: None

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
