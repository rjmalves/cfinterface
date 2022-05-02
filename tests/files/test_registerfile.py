from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.components.state import ComponentState
from cfinterface.data.registerdata import RegisterData
from cfinterface.files.registerfile import RegisterFile

from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


class DummyRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])


def test_registerfile_eq():
    rf1 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    rf2 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    assert rf1 == rf2


def test_registerfile_not_eq_invalid_type():
    rf1 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    rf2 = 5
    assert rf1 != rf2


def test_registerfile_not_eq_different_length():
    bd = RegisterData(DummyRegister(data=-1))
    bd.append(DummyRegister(data=+1))
    rf1 = RegisterFile(data=bd)
    rf2 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    assert rf1 != rf2


def test_registerfile_not_eq_valid():
    rf1 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    rf2 = RegisterFile(data=RegisterData(DummyRegister(data=+1)))
    assert rf1 != rf2


def test_registerfile_read():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    RegisterFile.REGISTERS = [DummyRegister]
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        f = RegisterFile.read("", "")
        assert len(f.data) == 2
        assert f.data.last.data[0] == data


def test_registerfile_write():
    data = "Hello, world!"
    bd = RegisterData(
        DummyRegister(state=ComponentState.READ_SUCCESS, data=[data])
    )
    RegisterFile.REGISTERS = [DummyRegister]
    f = RegisterFile(bd)
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        f.write("", "")
    m().write.assert_called_once_with(
        DummyRegister.IDENTIFIER + " " + data + "\n"
    )
