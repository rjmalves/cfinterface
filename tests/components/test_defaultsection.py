from cfinterface.components.defaultsection import DefaultSection
from cfinterface.components.state import ComponentState
from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


def test_default_section_eq():
    b1 = DefaultSection(data=0)
    b2 = DefaultSection(data=0)
    assert b1 == b2
    b1.data = 1
    assert b1 != b2


def test_default_section_read():
    data = "Hello, world!\n"
    m: MagicMock = mock_open(read_data=data)
    with patch("builtins.open", m):
        with open("", "r") as fp:
            b = DefaultSection()
            b.read_section(fp)
            assert b.data == data
            assert b.success


def test_default_section_write():
    data = "Hello, world!"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "w") as fp:
            b = DefaultSection(state=ComponentState.READ_SUCCESS)
            b.data = data
            b.write_section(fp)
    m().write.assert_called_once_with(data)
