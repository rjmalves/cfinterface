from cfinterface.adapters.line.delimitedrepository import DelimitedRepository
from cfinterface.components.literalfield import LiteralField


def test_delimitedrepository_read_no_fields():
    repo = DelimitedRepository([])
    fileline = ""
    assert len(repo.read(fileline)) == 0


def test_delimitedrepository_read_with_fields():
    fields = [LiteralField(6, 0), LiteralField(6, 7)]
    repo = DelimitedRepository(fields)
    fileline = "hello,;world!"
    values = repo.read(fileline)
    assert values[0] == "hello,"
    assert values[1] == "world!"


def test_delimitedrepository_write_no_fields():
    repo = DelimitedRepository([])
    assert len(repo.write([])) == 1


def test_delimitedrepository_write_with_fields():
    fields = [LiteralField(6, 0), LiteralField(6, 7)]
    values = ["hello,", "world!"]
    repo = DelimitedRepository(fields, values)
    fileline = "hello,;world!\n"
    outline = repo.write(values)
    assert fileline == outline
