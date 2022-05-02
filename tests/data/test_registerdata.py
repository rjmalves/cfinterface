from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.data.registerdata import RegisterData


class DummyRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])


def test_registerdata_eq():
    rd1 = RegisterData(DummyRegister(data=-1))
    rd2 = RegisterData(DummyRegister(data=-1))
    assert rd1 == rd2


def test_registerdata_not_eq():
    rd1 = RegisterData(DummyRegister(data=-1))
    rd2 = RegisterData(DummyRegister(data=+1))
    assert rd1 != rd2


def test_registerdata_append():
    rd = RegisterData(DummyRegister(data=-1))
    n_registers = 10
    for i in range(n_registers):
        rd.append(DummyRegister(data=i))
    assert len(rd) == n_registers + 1
    assert rd.first.data == -1
    assert rd.last.data == n_registers - 1


def test_registerdata_preppend():
    rd = RegisterData(DummyRegister(data=-1))
    n_registers = 10
    for i in range(n_registers):
        rd.preppend(DummyRegister(data=i))
    assert len(rd) == n_registers + 1
    assert rd.first.data == n_registers - 1
    assert rd.last.data == -1


def test_registerdata_add_before():
    rd = RegisterData(DummyRegister(data=-1))
    r1 = DummyRegister(data=1)
    rd.append(r1)
    r2 = DummyRegister(data=2)
    rd.add_before(r1, r2)
    assert r1.previous == r2
    assert r2.next == r1


def test_registerdata_add_after():
    rd = RegisterData(DummyRegister(data=-1))
    r1 = DummyRegister(data=1)
    rd.append(r1)
    r2 = DummyRegister(data=2)
    rd.add_after(r1, r2)
    assert r1.next == r2
    assert r2.previous == r1


def test_registerdata_remove():
    rd = RegisterData(DummyRegister(data=-1))
    r1 = DummyRegister(data=1)
    rd.append(r1)
    assert len(rd) == 2
    rd.remove(r1)
    assert len(rd) == 1


def test_registerdata_of_type():
    rd = RegisterData(DummyRegister())
    rd.append(Register())
    assert len(rd) == 2
    assert len([b for b in rd.of_type(DummyRegister)]) == 1
