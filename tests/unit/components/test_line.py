from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField


def test_line_read_no_fields():
    line = Line([])
    fileline = ""
    assert len(line.read(fileline)) == 0


def test_line_read_with_fields():
    fields = [LiteralField(6, 0), LiteralField(6, 7)]
    line = Line(fields)
    fileline = "hello, world!"
    values = line.read(fileline)
    assert values[0] == "hello,"
    assert values[1] == "world!"


def test_line_write_no_fields():
    line = Line([])
    assert len(line.write([])) == 1


def test_line_write_with_fields():
    fields = [LiteralField(6, 0), LiteralField(6, 7)]
    values = ["hello,", "world!"]
    line = Line(fields, values)
    fileline = "hello, world!\n"
    outline = line.write(values)
    assert fileline == outline


def test_line_read_no_fields_binary():
    line = Line([])
    fileline = b""
    assert len(line.read(fileline)) == 0


def test_line_read_with_fields_binary():
    fields = [LiteralField(6, 0), LiteralField(6, 7)]
    line = Line(fields, storage="BINARY")
    fileline = b"hello, world!"
    values = line.read(fileline)
    assert values[0] == "hello,"
    assert values[1] == "world!"


def test_line_write_no_fields_binary():
    line = Line([])
    assert len(line.write([])) == 1


def test_line_write_with_fields_binary():
    fields = [LiteralField(6, 0), LiteralField(6, 7)]
    values = ["hello,", "world!"]
    line = Line(fields, values, storage="BINARY")
    fileline = b"hello, world!"
    outline = line.write(values)
    assert fileline == outline
