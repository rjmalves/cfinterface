from typing import IO

from cfi.components.block import Block
from cfi.components.state import ComponentState

from unittest.mock import MagicMock, patch, mock_open


class DummyBlock(Block):
    BEGIN_PATTERN = "beg"
    END_PATTERN = "end"

    def read(self, file: IO) -> bool:
        self.data = file.readline().strip()

    def write(self, file: IO) -> bool:
        file.write(self.data)


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
