from datetime import datetime

import numpy as np
import pytest
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st

from cfinterface.components.datetimefield import DatetimeField
from cfinterface.components.floatfield import FloatField
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.literalfield import LiteralField


@st.composite
def integer_field_args(draw: st.DrawFn) -> tuple[int, int]:
    """Generate (size, value) pairs for IntegerField textual round-trip.

    Size from {2, 4, 8}; value constrained to fit within size characters
    (including optional minus sign).
    """
    size = draw(st.sampled_from([2, 4, 8]))
    dtype = {2: np.int16, 4: np.int32, 8: np.int64}[size]
    info = np.iinfo(dtype)
    # Maximum positive value that fits in `size` characters: 10^size - 1
    text_max = 10**size - 1
    # Minimum negative value that fits in `size` characters: -(10^(size-1) - 1)
    # e.g. size=2: -9 (1 digit + minus), size=4: -999, size=8: -9999999
    text_min = -(10 ** (size - 1) - 1)
    lo = max(info.min, text_min)
    hi = min(info.max, text_max)
    value = draw(st.integers(min_value=lo, max_value=hi))
    return size, value


@st.composite
def integer_field_binary_args(draw: st.DrawFn) -> tuple[int, int]:
    """Generate (size, value) pairs for IntegerField binary round-trip.

    Size from {2, 4, 8}; value constrained to the full numpy dtype range.
    """
    size = draw(st.sampled_from([2, 4, 8]))
    dtype = {2: np.int16, 4: np.int32, 8: np.int64}[size]
    info = np.iinfo(dtype)
    value = draw(st.integers(min_value=int(info.min), max_value=int(info.max)))
    return size, value


@st.composite
def float_field_f_args(draw: st.DrawFn) -> tuple[int, int, float]:
    """Generate (size, dec, value) args for FloatField F-format round-trip.

    Size in [5, 16] to accommodate value and decimals. Round-trip is exact
    within decimal_digits tolerance.
    """
    size = draw(st.integers(min_value=5, max_value=16))
    dec = draw(st.integers(min_value=1, max_value=min(6, size - 2)))
    value = draw(
        st.floats(
            min_value=-9999.0,
            max_value=9999.0,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    return size, dec, value


@st.composite
def float_field_binary_args(draw: st.DrawFn) -> tuple[int, float]:
    """Generate (size, value) pairs for FloatField binary round-trip.

    Size from {4, 8} (float32, float64); float16 excluded due to precision.
    """
    size = draw(st.sampled_from([4, 8]))
    dtype = {4: np.float32, 8: np.float64}[size]
    finfo = np.finfo(dtype)
    value = draw(
        st.floats(
            min_value=float(finfo.min),
            max_value=float(finfo.max),
            allow_nan=False,
            allow_infinity=False,
        )
    )
    return size, value


@st.composite
def literal_field_args(draw: st.DrawFn) -> tuple[int, str]:
    """Generate (size, value) pairs for LiteralField textual round-trip.

    Values are restricted to non-whitespace characters (L, N, P, S categories)
    since _textual_read strips leading/trailing whitespace.
    """
    size = draw(st.integers(min_value=1, max_value=40))
    value = draw(
        st.text(
            alphabet=st.characters(
                whitelist_categories=("L", "N", "P", "S"),
            ),
            min_size=1,
            max_size=size,
        )
    )
    return size, value


@pytest.mark.slow
@settings(max_examples=200)
@given(args=integer_field_args())
@example(args=(2, 0))
@example(args=(4, -1))
@example(args=(8, 99999999))
@example(args=(4, -999))
def test_integerfield_textual_roundtrip(args: tuple[int, int]) -> None:
    """IntegerField textual write then read recovers the original integer."""
    size, value = args
    field = IntegerField(size, 0, value=value)
    line = field.write("")
    # Line length must equal `size` when starting_position=0
    assert len(line) == size
    field2 = IntegerField(size, 0)
    field2.read(line)
    assert field2.value == value


@pytest.mark.slow
@settings(max_examples=200)
@given(args=integer_field_binary_args())
@example(args=(2, 0))
@example(args=(4, -1))
@example(args=(8, 0))
@example(args=(2, 32767))
@example(args=(2, -32768))
def test_integerfield_binary_roundtrip(args: tuple[int, int]) -> None:
    """IntegerField binary write then read recovers the original integer."""
    size, value = args
    field = IntegerField(size, 0, value=value)
    line = field.write(b"")
    assert len(line) == size
    field2 = IntegerField(size, 0)
    field2.read(line)
    assert field2.value == value


@pytest.mark.slow
@settings(max_examples=200)
@given(args=float_field_f_args())
@example(args=(8, 4, 0.0))
@example(args=(8, 4, -0.0))
@example(args=(5, 2, 0.0))
@example(args=(5, 1, -1.0))
def test_floatfield_textual_roundtrip_f_format(
    args: tuple[int, int, float],
) -> None:
    """FloatField format-F write then read recovers value within tolerance.

    Uses assume() to skip cases where the formatted value overflows the field
    width at full precision — the implementation reduces decimal digits in that
    case, which changes the effective tolerance. Only test when the initial
    format at full precision already fits.
    """
    size, dec, value = args
    # Skip if the value at full precision already exceeds the field width;
    # the writer reduces decimal digits in that case, so the round-trip
    # tolerance would need to be based on the reduced precision, not `dec`.
    initial_formatted = f"{round(value, dec):.{dec}F}"
    assume(len(initial_formatted) <= size)
    field = FloatField(size, 0, dec, format="F", value=value)
    written = field._textual_write()
    # Sanity: the written value must fill the field exactly
    assert len(written) == size
    line = field.write("")
    assert len(line) == size
    field2 = FloatField(size, 0, dec, format="F")
    field2.read(line)
    recovered = field2.value
    assert recovered is not None
    tolerance = 10 ** (-dec)
    assert abs(recovered - value) <= tolerance, (
        f"size={size} dec={dec} value={value} "
        f"written={written!r} recovered={recovered}"
    )


@pytest.mark.slow
@settings(max_examples=200)
@given(args=float_field_binary_args())
@example(args=(4, 0.0))
@example(args=(8, 0.0))
@example(args=(4, -0.0))
@example(args=(4, 1.0))
@example(args=(8, -1.0))
def test_floatfield_binary_roundtrip(args: tuple[int, float]) -> None:
    """FloatField binary write then read recovers float within dtype precision.

    The expected value is reconstructed via numpy to account for dtype
    conversion (e.g. float64 -> float32 precision loss).
    """
    size, value = args
    field = FloatField(size, 0, value=value)
    line = field.write(b"")
    assert len(line) == size
    field2 = FloatField(size, 0)
    field2.read(line)
    recovered = field2.value
    assert recovered is not None
    dtype = {4: np.float32, 8: np.float64}[size]
    # Reconstruct via numpy to get exact expected value after dtype conversion
    expected = float(np.array([value], dtype=dtype)[0])
    assert recovered == expected, (
        f"size={size} value={value} expected={expected} recovered={recovered}"
    )


@pytest.mark.slow
@settings(max_examples=200)
@given(args=literal_field_args())
@example(args=(5, "hello"))
@example(args=(1, "A"))
@example(args=(10, "abc123"))
def test_literalfield_textual_roundtrip(args: tuple[int, str]) -> None:
    """LiteralField textual write then read recovers the original string.

    _textual_write left-justifies within size, _textual_read strips — so
    the round-tripped value equals the original stripped value.
    """
    size, value = args
    field = LiteralField(size, 0, value=value)
    line = field.write("")
    assert len(line) == size
    field2 = LiteralField(size, 0)
    field2.read(line)
    # The value is written left-justified (ljust) and read back stripped,
    # so we compare against the stripped original (already stripped by strategy)
    assert field2.value == value.strip()


@pytest.mark.slow
@settings(max_examples=200)
@given(
    dt=st.datetimes(
        min_value=datetime(1900, 1, 1),
        max_value=datetime(2099, 12, 31),
    )
)
@example(dt=datetime(1900, 1, 1))
@example(dt=datetime(2099, 12, 31))
@example(dt=datetime(2000, 2, 29))
def test_datetimefield_textual_roundtrip(dt: datetime) -> None:
    """DatetimeField textual write then read recovers the original date.

    Only date components are preserved; time components are zeroed out
    since the format is "%Y/%m/%d" (10 chars).
    """
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    field = DatetimeField(10, 0, format="%Y/%m/%d", value=dt)
    line = field.write("")
    assert len(line) == 10
    field2 = DatetimeField(10, 0, format="%Y/%m/%d")
    field2.read(line)
    assert field2.value == dt
