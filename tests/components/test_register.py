from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.components.state import ComponentState
from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


class DummyRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])


def test_single_register_success():
    r1 = Register(state=ComponentState.READ_SUCCESS)
    assert r1.success


def test_single_register_not_found_error():
    r1 = Register(state=ComponentState.NOT_FOUND)
    assert not r1.success


def test_single_register_read_error():
    r1 = Register(state=ComponentState.READ_ERROR)
    assert not r1.success


def test_single_register_properties():
    r1 = Register()
    assert r1.is_first
    assert r1.is_last


def test_register_simple_chain_properties():
    # Build a simple register chain
    r1 = Register()
    r2 = Register()
    r3 = Register()
    # Sets relationships
    r1.next = r2
    r2.previous = r1
    r2.next = r3
    r3.previous = r2
    # Asserts properties
    assert r1.is_first
    assert r3.is_last
    assert not r1.is_last
    assert not r2.is_first
    assert not r2.is_last
    assert not r3.is_first
    assert r1.empty
    assert r2.empty
    assert r3.empty


def test_dummy_register_equal():
    b1 = DummyRegister()
    b2 = DummyRegister()
    assert b1 == b2


def test_dummy_register_read():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "r") as fp:
            b = DummyRegister()
            b.read_register(fp)
            assert b.data[0] == data
            assert b.success


def test_dummy_register_write():
    data = "Hello, world!"
    write_data = DummyRegister.IDENTIFIER + " " + data + "\n"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "w") as fp:
            b = DummyRegister(state=ComponentState.READ_SUCCESS)
            b.data = [data]
            b.write_register(fp)
    m().write.assert_called_once_with(write_data)
