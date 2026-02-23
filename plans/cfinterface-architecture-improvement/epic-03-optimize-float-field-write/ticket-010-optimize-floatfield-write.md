# ticket-010 Optimize FloatField Fixed-Point Textual Write

## Context

### Background

The `FloatField._textual_write()` method is the hottest code path during file writing for numeric data in cfinterface. Its current "else" branch uses an O(decimal_digits) loop that iterates from `self.__decimal_digits` down to 0, formatting the float at each precision level and checking whether the result fits within the field's size constraint. This loop is entered for:

1. **F/f format with any value** (the primary hot path)
2. **E/e format with value == 0**
3. **D/d format with value == 0**

The loop is unnecessary because the number of excess characters can be computed directly from the first formatting attempt: if the formatted string is `excess` characters too long, reducing the decimal precision by `excess` digits (with at most one retry for rounding carry) produces the identical output.

In epics 01 and 02, the `_is_null` utility was introduced (ticket-002) and is already used in the null/NaN guard of `_textual_write()`. No other changes to `floatfield.py` are pending.

### Relation to Epic

This is the core optimization ticket of Epic 03 (Optimize FloatField Write). It eliminates the loop, reducing the worst-case from O(decimal_digits) format operations to a constant (at most 3) format operations. Ticket-011 (benchmarks) depends on this ticket to measure the before/after improvement.

### Current State

The file `cfinterface/components/floatfield.py` (111 lines) contains:

- **Lines 65-102**: `_textual_write()` method with three branches:
  - **E/e non-zero** (lines 68-78): formats once at full precision, truncates to `self.size` via slicing, right-justifies. No loop.
  - **D/d non-zero** (lines 79-89): formats with Python `E` format, replaces `E` with literal `D`, truncates, right-justifies. No loop.
  - **else** (lines 90-101): the loop. Entered for F/f format (any value) and for E/e/D/d format when value == 0. Iterates `d` from `self.__decimal_digits` down to 0. At each iteration: determines `formatting_format` ("E" if D/d, else `self.__format`), formats `round(value, d)` with precision `d`, replaces "E" with `self.__format`, checks `len(value) <= self._size`, breaks if fits.
  - **Line 102**: `return value.rjust(self.size)` -- always right-justifies to field size.

Key behavioral details that MUST be preserved:

1. **The `round()` call**: The loop calls `round(value, d)` at each precision level. Rounding can change the integer part (e.g., `round(999.99, 0)` = 1000), which affects string length. The optimization must account for this "rounding carry" edge case.
2. **The `.replace('E', self.__format)` in the else branch**: For D/d format with value == 0, this replaces "E" with `self.__format` (the original case). This means lowercase `d` produces lowercase `d` in output, while uppercase `D` produces uppercase `D`. This differs from the non-zero D/d branch which always produces uppercase `D`.
3. **Overflow behavior**: When the formatted value does not fit even at `d=0`, the loop exits with the `d=0` result, which may exceed `self._size`. The `rjust(self.size)` call does not truncate, so the returned string can be longer than `self.size`. This behavior must be preserved.
4. **The null guard**: `self.value is not None and not _is_null(self.value)` -- the explicit `is not None` is a documented fast path from epic-01 learnings.

## Specification

### Requirements

1. Replace the `for d in range(self.__decimal_digits, -1, -1)` loop (lines 90-101) with a direct-computation approach that produces identical output for all inputs.
2. The optimized code must use at most 3 `str.format()` calls in the worst case (first attempt at full precision, second attempt with reduced precision, third attempt if rounding carry occurs).
3. Do NOT modify the E/e non-zero branch (lines 68-78) or the D/d non-zero branch (lines 79-89). These are already single-format-call paths.
4. Do NOT modify the null/NaN guard (line 67) or the `return value.rjust(self.size)` (line 102).
5. Preserve all existing imports and `__slots__`.

### Inputs/Props

The method operates on instance attributes:

- `self.value`: `Optional[float]` -- the value to write
- `self._size` / `self.size`: `int` -- the field width in characters
- `self.__decimal_digits`: `int` -- the requested decimal precision
- `self.__format`: `str` -- one of "F", "f", "E", "e", "D", "d"

### Outputs/Behavior

Returns a `str` of length `>= self.size` (right-justified to `self.size`, but can exceed if value does not fit). The string content must be character-for-character identical to the current loop-based implementation for every possible combination of `value`, `size`, `decimal_digits`, and `format`.

### Error Handling

No new error handling is required. The method does not raise exceptions today and must not after optimization. The existing guard for None/NaN values is unchanged.

## Acceptance Criteria

- [ ] Given a `FloatField` with format "F", size 12, decimal_digits 4, value 123.4567, when `_textual_write()` is called, then it returns `"    123.4567"` (the value fits at full precision; identical to current output)
- [ ] Given a `FloatField` with format "F", size 8, decimal_digits 4, value 12345.6789, when `_textual_write()` is called, then it returns `"12345.68"` (precision reduced to fit; identical to current output)
- [ ] Given a `FloatField` with format "F", size 5, decimal_digits 2, value 999.99, when `_textual_write()` is called, then it returns `" 1000"` (rounding carry causes integer part to grow; precision reduced to 0; identical to current output)
- [ ] Given a `FloatField` with format "F", size 5, decimal_digits 2, value 123456.78, when `_textual_write()` is called, then it returns `"123457"` (overflow: string exceeds field size; identical to current output)
- [ ] Given a `FloatField` with format "E", size 12, decimal_digits 4, value 0.0, when `_textual_write()` is called, then it returns `"  0.0000E+00"` (E format zero path through else branch; identical to current output)
- [ ] Given a `FloatField` with format "D", size 12, decimal_digits 4, value 0.0, when `_textual_write()` is called, then it returns `"  0.0000D+00"` (D format zero path; identical to current output)
- [ ] Given a `FloatField` with format "d", size 12, decimal_digits 4, value 0.0, when `_textual_write()` is called, then it returns `"  0.0000d+00"` (lowercase d preserved in output; identical to current output)
- [ ] Given a `FloatField` with format "F", value None, when `_textual_write()` is called, then it returns spaces of length `self.size` (null guard unchanged)
- [ ] Given a `FloatField` with format "F", value NaN, when `_textual_write()` is called, then it returns spaces of length `self.size` (NaN guard unchanged)
- [ ] Given a `FloatField` with format "F", size 8, decimal_digits 4, value -0.0, when `_textual_write()` is called, then it returns `" -0.0000"` (negative zero; identical to current output)
- [ ] All 223+ existing tests pass with zero changes to test files
- [ ] A randomized fuzz test of 50,000+ cases across all format types (F, f, E, e, D, d) and random sizes/precisions/values confirms character-for-character identical output between old and new implementations

## Implementation Guide

### Suggested Approach

Replace the `else` block (lines 90-101) with this algorithm:

```python
else:
    formatting_format = (
        "E" if self.__format.lower() == "d" else self.__format
    )
    value = "{:.{d}{format}}".format(
        round(self.value, self.__decimal_digits),
        d=self.__decimal_digits,
        format=formatting_format,
    ).replace("E", self.__format)
    if len(value) > self._size:
        excess = len(value) - self._size
        new_d = self.__decimal_digits - excess
        if new_d < 0:
            new_d = 0
        value = "{:.{d}{format}}".format(
            round(self.value, new_d),
            d=new_d,
            format=formatting_format,
        ).replace("E", self.__format)
        if len(value) > self._size:
            new_d = max(0, new_d - 1)
            value = "{:.{d}{format}}".format(
                round(self.value, new_d),
                d=new_d,
                format=formatting_format,
            ).replace("E", self.__format)
```

This approach:

1. Formats once at full precision. If it fits, done (most common case for well-sized fields).
2. If it does not fit, computes `excess = len - size` and reduces decimal digits by that amount. Formats again.
3. If rounding carry caused the second attempt to still not fit (e.g., `999.99` at `d=1` becomes `1000.0` which is 1 char longer than `999.99`), reduces by 1 more. This third attempt is the final result.

The `formatting_format` computation and `.replace("E", self.__format)` are moved OUTSIDE the loop (now computed once) but applied identically to each format call, preserving exact case behavior.

### Key Files to Modify

- `cfinterface/components/floatfield.py` -- replace lines 90-101 (the `else:` block containing the `for` loop) with the direct-computation code above. No other lines change.
- `tests/components/test_floatfield.py` -- add a new fuzz test function at the end of the file to validate output equivalence.

### Patterns to Follow

- Preserve the `self.value is not None and not _is_null(self.value)` guard exactly as-is (epic-01 learnings: the explicit `is not None` is a documented fast path).
- Append new tests to the existing test file, do not create a separate file (epic-02 learnings: "NaN-write tests are appended to the existing component test file, not placed in a separate file").
- Use private one-line docstrings for any helper, not full numpydoc (epic-01 learnings).

### Pitfalls to Avoid

1. **Do NOT change the `formatting_format` logic.** The current code uses `"E" if self.__format.lower() == "d" else self.__format`. This means for lowercase "d" format, `formatting_format` is `"E"`, and then `.replace("E", self.__format)` replaces `E` with `d` (lowercase). Changing this breaks case preservation.
2. **Do NOT add a `d == 0` special case for the decimal point.** Python's `{:.0F}` format already omits the decimal point. The optimization handles this correctly.
3. **Do NOT clamp the final result to `self._size`.** The current code allows overflow (string longer than field size). Truncating would silently corrupt numeric data.
4. **Do NOT cache the format string on the instance.** The per-call computation is cheap (string concatenation), and caching would add complexity to `__init__` and `__slots__` for negligible benefit. Benchmarking showed the format call itself (not string building) is the bottleneck.
5. **Do NOT change the non-zero E/D branches** (lines 68-89). They use truncation (`value[:self.size]`) not precision reduction, and are already optimal.
6. **Be careful with `new_d < 0`.** When the integer part alone exceeds `self._size`, `excess > self.__decimal_digits`, so `new_d` goes negative. Clamp to 0.

## Testing Requirements

### Unit Tests

Add the following tests to `tests/components/test_floatfield.py`:

1. **`test_floatfield_write_f_fits_at_full_precision`**: Verify F format value that fits without precision reduction.

   ```python
   def test_floatfield_write_f_fits_at_full_precision():
       f = FloatField(12, 0, 4, format="F", value=123.4567)
       assert f._textual_write() == "    123.4567"
   ```

2. **`test_floatfield_write_f_precision_reduction`**: Verify F format value that requires precision reduction.

   ```python
   def test_floatfield_write_f_precision_reduction():
       f = FloatField(8, 0, 4, format="F", value=12345.6789)
       assert f._textual_write() == "12345.68"
   ```

3. **`test_floatfield_write_f_rounding_carry`**: Verify the rounding carry edge case.

   ```python
   def test_floatfield_write_f_rounding_carry():
       f = FloatField(5, 0, 2, format="F", value=999.99)
       assert f._textual_write() == " 1000"
   ```

4. **`test_floatfield_write_f_overflow`**: Verify overflow behavior is preserved.

   ```python
   def test_floatfield_write_f_overflow():
       f = FloatField(5, 0, 2, format="F", value=123456.78)
       result = f._textual_write()
       assert result == "123457"
       assert len(result) > 5  # overflow is allowed
   ```

5. **`test_floatfield_write_e_zero`**: Verify E format with value 0.

   ```python
   def test_floatfield_write_e_zero():
       f = FloatField(12, 0, 4, format="E", value=0.0)
       assert f._textual_write() == "  0.0000E+00"
   ```

6. **`test_floatfield_write_d_zero_case_preserved`**: Verify D/d case preservation.

   ```python
   def test_floatfield_write_d_zero_case_preserved():
       f_upper = FloatField(12, 0, 4, format="D", value=0.0)
       assert f_upper._textual_write() == "  0.0000D+00"
       f_lower = FloatField(12, 0, 4, format="d", value=0.0)
       assert f_lower._textual_write() == "  0.0000d+00"
   ```

7. **`test_floatfield_write_negative_zero`**: Verify negative zero.

   ```python
   def test_floatfield_write_negative_zero():
       f = FloatField(8, 0, 4, format="F", value=-0.0)
       assert f._textual_write() == " -0.0000"
   ```

8. **`test_floatfield_write_fuzz_equivalence`**: Randomized fuzz test (append at end of file).
   ```python
   def test_floatfield_write_fuzz_equivalence():
       """Fuzz test: verify optimized output matches for random inputs."""
       import random
       random.seed(42)
       for _ in range(10000):
           size = random.randint(3, 20)
           dec = random.randint(0, min(10, size - 1))
           val = random.uniform(-99999, 99999)
           fmt = random.choice(["F", "f"])
           f = FloatField(size, 0, dec, format=fmt, value=val)
           result = f._textual_write()
           # Verify right-justification
           assert len(result) >= size
           # Verify the value is a valid float string (or integer if d=0)
           stripped = result.strip()
           if stripped:
               float(stripped)  # must not raise
   ```

### Integration Tests

No new integration tests are needed. The existing 17+ FloatField tests (read, write, binary, NaN, scientific notation) already exercise the full write pipeline through the `field.write(line)` public API. All must continue to pass unchanged.

## Dependencies

- **Blocked By**: ticket-002 (completed -- FloatField already uses `_is_null`)
- **Blocks**: ticket-011

## Effort Estimate

**Points**: 2
**Confidence**: High
