from typing import IO

import pytest

from cfinterface.components.block import Block
from cfinterface.components.state import ComponentState
from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


class DummyBlock(Block):
    BEGIN_PATTERN = "beg"
    END_PATTERN = "end"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data

    def read(self, file: IO) -> bool:
        self.data = file.readline().strip()
        return True

    def write(self, file: IO) -> bool:
        file.write(self.data)
        return True


def test_single_block_success():
    b1 = Block(state=ComponentState.READ_SUCCESS)
    assert b1.success


def test_single_block_not_found_error():
    b1 = Block(state=ComponentState.NOT_FOUND)
    assert not b1.success


def test_single_block_read_error():
    b1 = Block(state=ComponentState.READ_ERROR)
    assert not b1.success


def test_single_block_properties():
    b1 = Block()
    assert b1.is_first
    assert b1.is_last


def test_block_simple_chain_properties():
    # Build a simple block chain
    b1 = Block()
    b2 = Block()
    b3 = Block()
    # Sets relationships
    b1.next = b2
    b2.previous = b1
    b2.next = b3
    b3.previous = b2
    # Asserts properties
    assert b1.is_first
    assert b3.is_last
    assert not b1.is_last
    assert not b2.is_first
    assert not b2.is_last
    assert not b3.is_first
    assert b1.empty
    assert b2.empty
    assert b3.empty


def test_block_equal_error():
    b1 = Block()
    b2 = Block()
    with pytest.raises(NotImplementedError):
        b1 == b2


def test_block_read_error():
    b = Block()
    with pytest.raises(NotImplementedError):
        m: MagicMock = mock_open(read_data="")
        with patch("builtins.open", m):
            with open("", "r") as fp:
                b.read_block(fp)


def test_block_write_error():
    b = Block(state=ComponentState.READ_SUCCESS)
    with pytest.raises(NotImplementedError):
        m: MagicMock = mock_open(read_data="")
        with patch("builtins.open", m):
            with open("", "r") as fp:
                b.write_block(fp)


def test_dummy_block_equal():
    b1 = DummyBlock()
    b2 = DummyBlock()
    assert b1 == b2


def test_dummy_block_read():
    data = "Hello, world!"
    filedata = (
        "\n".join([DummyBlock.BEGIN_PATTERN, data, DummyBlock.END_PATTERN])
        + "\n"
    )
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "r") as fp:
            b = DummyBlock()
            assert DummyBlock.begins(fp.readline())
            b.read_block(fp)
            assert b.data == data
            assert b.success
            assert DummyBlock.ends(fp.readline())


def test_dummy_block_write():
    data = "Hello, world!"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "w") as fp:
            b = DummyBlock(state=ComponentState.READ_SUCCESS)
            b.data = data
            b.write_block(fp)
    m().write.assert_called_once_with(data)
