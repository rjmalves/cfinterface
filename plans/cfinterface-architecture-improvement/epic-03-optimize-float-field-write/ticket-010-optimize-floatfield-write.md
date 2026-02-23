# ticket-010 Optimize FloatField Fixed-Point Textual Write

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Replace the O(decimal_digits) precision-reduction loop in `FloatField._textual_write()` (lines 94-102 of `cfinterface/components/floatfield.py`) with a direct formatting approach that computes the maximum decimal digits that fit within the field size constraint in a single calculation, avoiding iteration.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/components/floatfield.py`, `tests/components/test_floatfield.py`
- **Key decisions needed**: Whether to use `f-string` direct formatting or a pre-computed format string cached at `__init__` time; how to handle the edge case where `value == 0` and format is `"F"` (currently falls through to the loop)
- **Open questions**:
  - Can the maximum precision be computed as `field_size - integer_digits - 1` (for the decimal point) in all cases?
  - Does the `round()` call before formatting affect the output when precision is reduced?
  - Should the format string be cached on the field instance for repeated writes, or is a per-call computation sufficient?

## Dependencies

- **Blocked By**: ticket-002 (FloatField will have been modified to use `_is_null`)
- **Blocks**: ticket-011

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
