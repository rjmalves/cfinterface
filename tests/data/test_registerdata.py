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


class DefaultRegister(Register):
    IDENTIFIER = "def"
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


def test_registerdata_getitem():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    r1 = DummyRegister(data=1)
    r2 = DummyRegister(data=2)
    r3 = DummyRegister(data=3)
    rd.append(r1)
    rd.append(r2)
    rd.append(r3)
    assert rd[0] is root
    assert rd[1] is r1
    assert rd[3] is r3


def test_registerdata_getitem_negative():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    r1 = DummyRegister(data=1)
    rd.append(r1)
    assert rd[-1] is r1


def test_registerdata_getitem_out_of_bounds():
    rd = RegisterData(DummyRegister(data=0))
    try:
        _ = rd[100]
        assert False, "Expected IndexError"
    except IndexError:
        pass


def test_registerdata_len_is_o1():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    for i in range(1000):
        rd.append(DummyRegister(data=i))
    assert len(rd) == 1001


def test_registerdata_remove_updates_pointers():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    r1 = DummyRegister(data=1)
    r2 = DummyRegister(data=2)
    r3 = DummyRegister(data=3)
    rd.append(r1)
    rd.append(r2)
    rd.append(r3)
    rd.remove(r2)
    assert r1.next is r3
    assert r3.previous is r1


def test_registerdata_remove_head():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    r1 = DummyRegister(data=1)
    rd.append(r1)
    rd.remove(r1)
    assert rd.last is root
    assert root.next is None


def test_registerdata_iteration_order():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    appended = []
    for i in range(1, 6):
        r = DummyRegister(data=i)
        rd.append(r)
        appended.append(r)
    expected = [root] + appended
    assert list(rd) == expected


def test_registerdata_computed_previous_next():
    root = DummyRegister(data=0)
    r1 = DummyRegister(data=1)
    r2 = DummyRegister(data=2)
    rd = RegisterData(root)
    rd.append(r1)
    rd.append(r2)
    assert r1.previous is root
    assert r1.next is r2
    assert root.previous is None
    assert r2.next is None


def test_registerdata_computed_after_remove():
    root = DummyRegister(data=0)
    r1 = DummyRegister(data=1)
    r2 = DummyRegister(data=2)
    rd = RegisterData(root)
    rd.append(r1)
    rd.append(r2)
    rd.remove(r1)
    assert root.next is r2
    assert r2.previous is root
    assert r1._container is None


def test_registerdata_of_type_with_mixed_types():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    defaults = []
    for i in range(1, 6):
        d = DummyRegister(data=i)
        rd.append(d)
        rd.append(DefaultRegister(data=i))
        defaults.append(d)
    dummy_results = list(rd.of_type(DummyRegister))
    assert len(dummy_results) == 6
    assert dummy_results[0] is root
    for expected, actual in zip(defaults, dummy_results[1:]):
        assert actual is expected
    default_results = list(rd.of_type(DefaultRegister))
    assert len(default_results) == 5
    assert all(type(r) is DefaultRegister for r in default_results)


def test_registerdata_of_type_base_class():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    for i in range(1, 6):
        rd.append(DummyRegister(data=i))
        rd.append(DefaultRegister(data=i))
    all_results = list(rd.of_type(Register))
    assert len(all_results) == 11
    items_from_iter = list(rd)
    assert all_results == items_from_iter


def test_registerdata_type_index_after_remove():
    root = DummyRegister(data=0)
    r1 = DummyRegister(data=1)
    r2 = DefaultRegister(data=2)
    rd = RegisterData(root)
    rd.append(r1)
    rd.append(r2)
    rd.remove(r1)
    dummy_results = list(rd.of_type(DummyRegister))
    assert len(dummy_results) == 1
    assert dummy_results[0] is root
    default_results = list(rd.of_type(DefaultRegister))
    assert len(default_results) == 1
    assert default_results[0] is r2
    assert rd._type_index[DefaultRegister] == [1]


def test_registerdata_type_index_after_preppend():
    root = DummyRegister(data=0)
    rd = RegisterData(root)
    rd.append(DefaultRegister(data=1))
    new = DummyRegister(data=2)
    rd.preppend(new)
    dummy_results = list(rd.of_type(DummyRegister))
    assert len(dummy_results) == 2
    assert dummy_results[0] is new
    assert dummy_results[1] is root
    assert rd._type_index[DummyRegister] == [0, 1]
    assert rd._type_index[DefaultRegister] == [2]
