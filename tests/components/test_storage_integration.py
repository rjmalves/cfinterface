from cfinterface.components.block import Block
from cfinterface.components.register import Register
from cfinterface.storage import StorageType


def test_register_matches_with_enum():
    class TestReg(Register):
        IDENTIFIER = "TEST"
        IDENTIFIER_DIGITS = 4

    assert TestReg.matches("TEST data", StorageType.TEXT)
    assert not TestReg.matches("OTHER data", StorageType.TEXT)


def test_block_begins_with_enum():
    class TestBlock(Block):
        BEGIN_PATTERN = "BEGIN"

    assert TestBlock.begins("BEGIN of block", StorageType.TEXT)
