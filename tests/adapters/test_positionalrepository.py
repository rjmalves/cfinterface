from cfinterface.adapters.line.positionalrepository import PositionalRepository
from cfinterface.components.literalfield import LiteralField


def test_positionalrepository_read_no_fields():
    repo = PositionalRepository([])
    fileline = ""
    assert len(repo.read(fileline)) == 0


def test_positionalrepository_read_with_fields():
    fields = [LiteralField(6, 0), LiteralField(6, 7)]
    repo = PositionalRepository(fields)
    fileline = "hello, world!"
    values = repo.read(fileline)
    assert values[0] == "hello,"
    assert values[1] == "world!"


def test_positionalrepository_write_no_fields():
    repo = PositionalRepository([])
    assert len(repo.write([])) == 1


def test_positionalrepository_write_with_fields():
    fields = [LiteralField(6, 0), LiteralField(6, 7)]
    values = ["hello,", "world!"]
    repo = PositionalRepository(fields, values)
    fileline = "hello, world!\n"
    outline = repo.write(values)
    assert fileline == outline
