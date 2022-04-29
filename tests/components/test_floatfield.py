from cfinterface.components.floatfield import FloatField


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
