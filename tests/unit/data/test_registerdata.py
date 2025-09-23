from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.data.registerdata import RegisterData


class DummyRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])

    @property
    def my_data(self):
        return self.data[0]


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
    assert rd.last == r1
    assert len(rd) == 3


def test_registerdata_add_before_root():
    r1 = DummyRegister(data=-1)
    rd = RegisterData(r1)
    r2 = DummyRegister(data=2)
    rd.add_before(r1, r2)
    assert r1.previous == r2
    assert r2.next == r1
    assert rd.last == r1
    assert len(rd) == 2


def test_registerdata_add_after():
    rd = RegisterData(DummyRegister(data=-1))
    r1 = DummyRegister(data=1)
    rd.append(r1)
    r2 = DummyRegister(data=2)
    rd.add_after(r1, r2)
    assert r1.next == r2
    assert r2.previous == r1
    assert rd.last == r2
    assert len(rd) == 3


def test_registerdata_add_after_head():
    r1 = DummyRegister(data=-1)
    rd = RegisterData(r1)
    r2 = DummyRegister(data=2)
    rd.add_after(r1, r2)
    assert r1.next == r2
    assert r2.previous == r1
    assert rd.last == r2
    assert len(rd) == 2


def test_registerdata_remove():
    rd = RegisterData(DummyRegister(data=-1))
    r1 = DummyRegister(data=1)
    rd.append(r1)
    assert len(rd) == 2
    rd.remove(r1)
    assert len(rd) == 1


def test_registerdata_of_type():
    rd = RegisterData(DummyRegister())
    rd.append(DummyRegister())
    assert len(rd) == 2
    assert len([b for b in rd.of_type(DummyRegister)]) == 2


def test_registerdata_get_registers_of_type_no_filter():
    r1 = DummyRegister(data=[10])
    rd = RegisterData(r1)
    rd.append(Register())
    assert rd.get_registers_of_type(DummyRegister) == r1


def test_registerdata_get_registers_of_type_filter():
    r1 = DummyRegister(data=[10])
    rd = RegisterData(r1)
    rd.append(DummyRegister())
    rd.append(DummyRegister(data=[11]))
    assert len(rd.get_registers_of_type(DummyRegister)) == 3
    assert rd.get_registers_of_type(DummyRegister, my_data=10) == r1


def test_registerdata_remove_registers_of_type_no_filter():
    r1 = DummyRegister(data=[10])
    rd = RegisterData(r1)
    rd.append(DummyRegister())
    rd.append(DummyRegister(data=[11]))
    rd.remove_registers_of_type(DummyRegister)
    assert len(rd) == 1
