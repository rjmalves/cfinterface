from cfinterface.components.literalfield import LiteralField


def test_literalfield_read():
    data = "field"
    field = LiteralField(len(data), 0)
    line = f"{data}-something-else"
    field.read(line)
    assert field.value == data


def test_literalfield_write():
    line_before = "field-something-else"
    data = line_before[6:15]
    field = LiteralField(len(data), 6, value=data)
    line_after = field.write(line_before)
    assert line_before == line_after


def test_literalfield_write_empty():
    field = LiteralField(5, 0)
    assert len(field.write("")) == 5


def test_literalfield_write_short_line():
    line_before = "field-something-else"
    data = line_before[6:15]
    field = LiteralField(len(data), 6, value=data)
    line_after = field.write("   ")
    assert data == line_after[6:]
