from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


class DummyRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])

    @property
    def custom_property(self) -> str:
        return "Custom!"


class DummyDelimitedRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)], delimiter=";")


class DummyBinaryRegister(Register):
    LINE = Line([LiteralField(13)], storage="BINARY")


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


def test_dummy_register_custom_properties():
    assert DummyRegister().custom_properties == ["custom_property"]


def test_dummy_delimitedregister_custom_properties():
    assert DummyDelimitedRegister().custom_properties == []


def test_dummy_register_read():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "r") as fp:
            b = DummyRegister()
            b.read_register(fp)
            assert b.data[0] == data


def test_dummy_register_write():
    data = "Hello, world!"
    write_data = DummyRegister.IDENTIFIER + " " + data + "\n"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "w") as fp:
            b = DummyRegister()
            b.data = [data]
            b.write_register(fp)
    m().write.assert_called_once_with(write_data)


def test_dummy_delimiterregister_read():
    data = "Hello, world!"
    filedata = DummyDelimitedRegister.IDENTIFIER + " ;" + data + "\n"
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "r") as fp:
            b = DummyDelimitedRegister()
            b.read_register(fp)
            assert b.data[0] == data


def test_dummy_delimiterregister_write():
    data = "Hello, world!"
    write_data = DummyDelimitedRegister.IDENTIFIER + ";" + data + "\n"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "w") as fp:
            b = DummyDelimitedRegister()
            b.data = [data]
            b.write_register(fp)
    m().write.assert_called_once_with(write_data)


def test_dummy_binaryregister_read():
    data = "Hello, world!"
    filedata = data.encode("utf-8")
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "rb") as fp:
            b = DummyBinaryRegister()
            b.read_register(fp, storage="BINARY")
            assert b.data[0] == data


def test_dummy_binaryregister_write():
    data = "Hello, world!"
    write_data = data.encode("utf-8")
    filedata = b""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "wb") as fp:
            b = DummyBinaryRegister()
            b.data = [data]
            b.write_register(fp, storage="BINARY")
    m().write.assert_called_once_with(write_data)
