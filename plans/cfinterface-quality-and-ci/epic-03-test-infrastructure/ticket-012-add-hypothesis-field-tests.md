# ticket-012 Add Hypothesis Property-Based Tests for Field Round-Trips

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Implement hypothesis property-based tests that verify read/write round-trip correctness for FloatField, IntegerField, DatetimeField, and LiteralField. These tests should generate random valid field values and verify that `field.write()` followed by `field.read()` preserves the value (within type-appropriate tolerance). This replaces the hand-rolled fuzz test in `test_floatfield.py` (50k random iterations) with a more principled approach that also covers the other field types.

## Anticipated Scope

- **Files likely to be modified**: `tests/components/test_floatfield_hypothesis.py` (create), `tests/components/test_integerfield_hypothesis.py` (create), `tests/components/test_datetimefield_hypothesis.py` (create), `tests/components/test_literalfield_hypothesis.py` (create), possibly `tests/conftest.py` (add hypothesis strategies)
- **Key decisions needed**: Whether to define hypothesis strategies as `@composite` functions in conftest.py or inline in test files, what value ranges to use for each field type (especially FloatField which has complex formatting), how to handle the existing fuzz test (remove vs. keep alongside hypothesis)
- **Open questions**: Should hypothesis tests replace the existing fuzz test or coexist? What `max_examples` setting to use (balance between thoroughness and CI runtime)? How should DatetimeField format strings be handled in the strategy?

## Dependencies

- **Blocked By**: ticket-006-add-py-typed-and-dev-deps (hypothesis must be installed), ticket-011-create-conftest-and-fixtures (shared fixtures/strategies)
- **Blocks**: None

## Effort Estimate

**Points**: 3
**Confidence**: Low (will be re-estimated during refinement)
