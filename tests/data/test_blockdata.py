from cfinterface.components.block import Block
from cfinterface.data.blockdata import BlockData


class DummyBlock(Block):
    BEGIN_PATTERN = "beg"
    END_PATTERN = "end"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data


def test_blockdata_eq():
    bd1 = BlockData(DummyBlock(data=-1))
    bd2 = BlockData(DummyBlock(data=-1))
    assert bd1 == bd2


def test_blockdata_not_eq():
    bd1 = BlockData(DummyBlock(data=-1))
    bd2 = BlockData(DummyBlock(data=+1))
    assert bd1 != bd2


def test_blockdata_append():
    bd = BlockData(DummyBlock(data=-1))
    n_blocks = 10
    for i in range(n_blocks):
        bd.append(DummyBlock(data=i))
    assert len(bd) == n_blocks + 1
    assert bd.first.data == -1
    assert bd.last.data == n_blocks - 1


def test_blockdata_preppend():
    bd = BlockData(DummyBlock(data=-1))
    n_blocks = 10
    for i in range(n_blocks):
        bd.preppend(DummyBlock(data=i))
    assert len(bd) == n_blocks + 1
    assert bd.first.data == n_blocks - 1
    assert bd.last.data == -1


def test_blockdata_add_before():
    bd = BlockData(DummyBlock(data=-1))
    b1 = DummyBlock(data=1)
    bd.append(b1)
    b2 = DummyBlock(data=2)
    bd.add_before(b1, b2)
    assert b1.previous == b2
    assert b2.next == b1


def test_blockdata_add_after():
    bd = BlockData(DummyBlock(data=-1))
    b1 = DummyBlock(data=1)
    bd.append(b1)
    b2 = DummyBlock(data=2)
    bd.add_after(b1, b2)
    assert b1.next == b2
    assert b2.previous == b1


def test_blockdata_remove():
    bd = BlockData(DummyBlock(data=-1))
    b1 = DummyBlock(data=1)
    bd.append(b1)
    assert len(bd) == 2
    bd.remove(b1)
    assert len(bd) == 1


def test_blockdata_of_type():
    bd = BlockData(DummyBlock())
    bd.append(Block())
    assert len(bd) == 2
    assert len([b for b in bd.of_type(DummyBlock)]) == 1
