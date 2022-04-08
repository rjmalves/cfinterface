from cfinterface.components.defaultblock import DefaultBlock
from cfinterface.components.state import ComponentState
from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


def test_default_block_eq():
    b1 = DefaultBlock(data=0)
    b2 = DefaultBlock(data=0)
    assert b1 == b2
    b1.data = 1
    assert b1 != b2


def test_default_block_read():
    data = "Hello, world!\n"
    m: MagicMock = mock_open(read_data=data)
    with patch("builtins.open", m):
        with open("", "r") as fp:
            b = DefaultBlock()
            b.read_block(fp)
            assert b.data == data
            assert b.success


def test_default_block_write():
    data = "Hello, world!"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "w") as fp:
            b = DefaultBlock(state=ComponentState.READ_SUCCESS)
            b.data = data
            b.write_block(fp)
    m().write.assert_called_once_with(data)
