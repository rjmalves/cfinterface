from cfinterface.components.integerfield import IntegerField


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
