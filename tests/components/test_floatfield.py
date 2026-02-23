from cfinterface.components.floatfield import FloatField

import numpy as np


def test_floatfield_read():
    data = 12345
    field = FloatField(5, 0, 1)
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == data


def test_floatfield_read_scientific_notation():
    data = "1.2e3"
    field = FloatField(5, 0, 1, format="e")
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == float(data)


def test_floatfield_read_scientific_notation_d():
    data = "1.2D3"
    field = FloatField(5, 0, 1, format="D")
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == float(data.replace("D", "e"))


def test_floatfield_comma_separator():
    data = "1,23"
    field = FloatField(4, 0, 1, sep=",")
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == 1.23


def test_floatfield_write():
    line_before = "field-12345-else"
    data = float(line_before[6:11])
    field = FloatField(5, 6, 1, value=data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_floatfield_write_empty():
    field = FloatField(5, 0, 1)
    assert len(field.write("")) == 5


def test_floatfield_write_short_line():
    line_before = "field-12345-else"
    data = float(line_before[6:11])
    field = FloatField(5, 6, 1, value=data)
    line_after = field.write("   ")
    assert data == float(line_after[6:])


def test_floatfield_write_scientific_notation():
    data_text = "1.2e+3"
    line_before = f"field-{data_text}-else"
    data = float(data_text)
    field = FloatField(5, 6, 1, format="e", value=data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_floatfield_write_scientific_notation_d():
    data_text = "1.2D+3"
    line_before = f"field-{data_text}-else"
    data = float(data_text.replace("D", "e"))
    field = FloatField(5, 6, 1, format="D", value=data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_floatfield_write_scientific_notation_0():
    data_text = "0e+00"
    line_before = f"field-{data_text}-else"
    data = float(data_text)
    field = FloatField(5, 6, 1, format="e", value=data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_floatfield_read_binary():
    data = 105.40
    field = FloatField(4, 0)
    line = np.array([data], dtype=np.float32).tobytes()
    field.read(line)
    assert round(field.value, 1) == data


def test_floatfield_write_binary():
    floatdata = 105.40
    line_before = (
        b"field-" + np.array([floatdata], dtype=np.float32).tobytes() + b"-else"
    )
    field = FloatField(4, 6, value=floatdata)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_floatfield_write_empty_binary():
    field = FloatField(4, 0)
    assert len(field.write(b"")) == 4


def test_floatfield_write_short_line_binary():
    floatdata = 105.40
    bytedata = np.array([floatdata], dtype=np.float32).tobytes()
    field = FloatField(4, 6, value=floatdata)
    line_after = field.write(b"   ")
    assert bytedata == line_after[6:]


def test_floatfield_write_nan_textual():
    field = FloatField(5, 0, 1, value=float("nan"))
    result = field.write("")
    assert result.strip() == ""
    assert len(result) == 5


def test_floatfield_write_nan_binary():
    field = FloatField(4, 0, value=float("nan"))
    result = field.write(b"")
    assert len(result) == 4


def test_floatfield_write_f_fits_at_full_precision():
    f = FloatField(12, 0, 4, format="F", value=123.4567)
    assert f._textual_write() == "    123.4567"


def test_floatfield_write_f_precision_reduction():
    f = FloatField(8, 0, 4, format="F", value=12345.6789)
    assert f._textual_write() == "12345.68"


def test_floatfield_write_f_rounding_carry():
    f = FloatField(5, 0, 2, format="F", value=999.99)
    assert f._textual_write() == " 1000"


def test_floatfield_write_f_overflow():
    f = FloatField(5, 0, 2, format="F", value=123456.78)
    result = f._textual_write()
    assert result == "123457"
    assert len(result) > 5


def test_floatfield_write_e_zero():
    f = FloatField(12, 0, 4, format="E", value=0.0)
    assert f._textual_write() == "  0.0000E+00"


def test_floatfield_write_d_zero_case_preserved():
    f_upper = FloatField(12, 0, 4, format="D", value=0.0)
    assert f_upper._textual_write() == "  0.0000D+00"
    f_lower = FloatField(12, 0, 4, format="d", value=0.0)
    assert f_lower._textual_write() == "  0.0000d+00"


def test_floatfield_write_negative_zero():
    f = FloatField(8, 0, 4, format="F", value=-0.0)
    assert f._textual_write() == " -0.0000"


def _reference_textual_write(value, size, decimal_digits, fmt):
    for d in range(decimal_digits, -1, -1):
        formatting_format = "E" if fmt.lower() == "d" else fmt
        result = "{:.{d}{format}}".format(
            round(value, d), d=d, format=formatting_format
        ).replace("E", fmt)
        if len(result) <= size:
            break
    return result.rjust(size)


def test_floatfield_write_fuzz_equivalence():
    """Fuzz test: verify optimized output matches reference for random inputs."""
    import random

    random.seed(42)
    for _ in range(50000):
        size = random.randint(3, 20)
        dec = random.randint(0, min(10, size - 1))
        val = random.uniform(-99999, 99999)
        fmt = random.choice(["F", "f", "E", "e", "D", "d"])
        f = FloatField(size, 0, dec, format=fmt, value=val)
        result = f._textual_write()
        if fmt.lower() in ("e", "d") and val != 0.0:
            continue  # non-zero E/D uses truncation branch, not the else block
        expected = _reference_textual_write(val, size, dec, fmt)
        assert result == expected, (
            f"Mismatch: fmt={fmt} size={size} dec={dec} val={val} "
            f"got={result!r} expected={expected!r}"
        )


def test_floatfield_benchmark_smoke():
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from benchmarks.bench_floatfield_write import _bench_scenario, _make_fields

    fields = _make_fields(12, 4, "F", [1.234, 5.678])
    name, n, mn, mean, mx = _bench_scenario("smoke", fields, 100, 1)
    assert name == "smoke"
    assert n == 100
    assert mn > 0
