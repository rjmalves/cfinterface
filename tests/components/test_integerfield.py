from cfinterface.components.integerfield import IntegerField
import numpy as np


def test_integerfield_read():
    data = 12345
    field = IntegerField(5, 0)
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == data


def test_integerfield_write():
    line_before = "field-12345-else"
    data = int(line_before[6:11])
    field = IntegerField(5, 6, value=data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_integerfield_write_empty():
    field = IntegerField(5, 0)
    assert len(field.write("")) == 5


def test_integerfield_write_short_line():
    line_before = "field-12345-else"
    data = int(line_before[6:11])
    field = IntegerField(5, 6, value=data)
    line_after = field.write("   ")
    assert str(data) == line_after[6:]


def test_integerfield_read_binary():
    data = 12345
    field = IntegerField(4, 0)
    line = np.array([data], dtype=np.int32).tobytes()
    field.read(line)
    assert field.value == data


def test_integerfield_write_binary():
    intdata = 12345
    line_before = (
        b"field-"
        + np.array([intdata], dtype=np.int32).tobytes()
        + b"12345-else"
    )
    field = IntegerField(4, 6, value=intdata)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_integerfield_write_empty_binary():
    field = IntegerField(4, 0)
    assert len(field.write(b"")) == 4


def test_integerfield_write_short_line_binary():
    intdata = 12345
    bytedata = np.array([intdata], dtype=np.int32).tobytes()
    field = IntegerField(4, 6, value=intdata)
    line_after = field.write(b"   ")
    assert bytedata == line_after[6:]
