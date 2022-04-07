from cfinterface.components.floatfield import FloatField

import pytest


def test_floatfield_read():
    data = 12345
    field = FloatField(5, 0, 1)
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == data


def test_floatfield_write():
    line_before = "field-12345-else"
    data = float(line_before[6:11])
    field = FloatField(5, 6, 1, value=data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_floatfield_write_error():
    with pytest.raises(ValueError):
        field = FloatField(5, 0, 1)
        field.write("")


def test_floatfield_write_short_line():
    line_before = "field-12345-else"
    data = float(line_before[6:11])
    field = FloatField(5, 6, 1, value=data)
    line_after = field.write("   ")
    assert data == float(line_after[6:])
