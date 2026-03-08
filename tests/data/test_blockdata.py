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

    @property
    def my_data(self):
        return self.data


class DefaultBlock(Block):
    BEGIN_PATTERN = "def_beg"
    END_PATTERN = "def_end"

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
    assert bd.last == b1
    assert len(bd) == 3


def test_blockdata_add_before_root():
    b1 = DummyBlock(data=-1)
    bd = BlockData(b1)
    b2 = DummyBlock(data=2)
    bd.add_before(b1, b2)
    assert b1.previous == b2
    assert b2.next == b1
    assert bd.last == b1
    assert len(bd) == 2


def test_blockdata_add_after():
    bd = BlockData(DummyBlock(data=-1))
    b1 = DummyBlock(data=1)
    bd.append(b1)
    b2 = DummyBlock(data=2)
    bd.add_after(b1, b2)
    assert b1.next == b2
    assert b2.previous == b1
    assert bd.last == b2
    assert len(bd) == 3


def test_blockdata_add_after_head():
    b1 = DummyBlock(data=-1)
    bd = BlockData(b1)
    b2 = DummyBlock(data=2)
    bd.add_after(b1, b2)
    assert b1.next == b2
    assert b2.previous == b1
    assert bd.last == b2
    assert len(bd) == 2


def test_blockdata_remove():
    bd = BlockData(DummyBlock(data=-1))
    b1 = DummyBlock(data=1)
    bd.append(b1)
    assert len(bd) == 2
    bd.remove(b1)
    assert len(bd) == 1


def test_blockdata_of_type():
    bd = BlockData(DummyBlock())
    bd.append(DummyBlock())
    assert len(bd) == 2
    assert len([b for b in bd.of_type(DummyBlock)]) == 2


def test_blockdata_get_blocks_of_type_no_filter():
    b1 = DummyBlock(data=10)
    bd = BlockData(b1)
    bd.append(Block())
    assert bd.get_blocks_of_type(DummyBlock) == b1


def test_blockdata_get_blocks_of_type_filter():
    b1 = DummyBlock(data=10)
    bd = BlockData(b1)
    bd.append(DummyBlock())
    bd.append(DummyBlock(data=11))
    assert len(bd.get_blocks_of_type(DummyBlock)) == 3
    assert bd.get_blocks_of_type(DummyBlock, my_data=10) == b1


def test_blockdata_remove_blocks_of_type_no_filter():
    b1 = DummyBlock(data=10)
    bd = BlockData(b1)
    bd.append(DummyBlock())
    bd.append(DummyBlock(data=11))
    bd.remove_blocks_of_type(DummyBlock)
    assert len(bd) == 1


def test_blockdata_getitem():
    root = DummyBlock(data=0)
    bd = BlockData(root)
    b1 = DummyBlock(data=1)
    b2 = DummyBlock(data=2)
    b3 = DummyBlock(data=3)
    bd.append(b1)
    bd.append(b2)
    bd.append(b3)
    assert bd[0] is root
    assert bd[3] is b3


def test_blockdata_getitem_negative():
    root = DummyBlock(data=0)
    bd = BlockData(root)
    b1 = DummyBlock(data=1)
    b2 = DummyBlock(data=2)
    bd.append(b1)
    bd.append(b2)
    assert bd[-1] is b2


def test_blockdata_getitem_out_of_bounds():
    bd = BlockData(DummyBlock(data=0))
    try:
        _ = bd[100]
        assert False, "Expected IndexError"
    except IndexError:
        pass


def test_blockdata_remove_updates_pointers():
    root = DummyBlock(data=0)
    bd = BlockData(root)
    b1 = DummyBlock(data=1)
    b2 = DummyBlock(data=2)
    b3 = DummyBlock(data=3)
    bd.append(b1)
    bd.append(b2)
    bd.append(b3)
    bd.remove(b2)
    assert b1.next is b3
    assert b3.previous is b1
    assert len(bd) == 3


def test_blockdata_remove_head():
    root = DummyBlock(data=0)
    bd = BlockData(root)
    b1 = DummyBlock(data=1)
    bd.append(b1)
    bd.remove(b1)
    assert bd.last is root
    assert root.next is None
    assert len(bd) == 1


def test_blockdata_computed_previous_next():
    root = DummyBlock(data=0)
    b1 = DummyBlock(data=1)
    b2 = DummyBlock(data=2)
    bd = BlockData(root)
    bd.append(b1)
    bd.append(b2)
    assert b1.previous is root
    assert b1.next is b2
    assert root.previous is None
    assert b2.next is None


def test_blockdata_computed_after_remove():
    root = DummyBlock(data=0)
    b1 = DummyBlock(data=1)
    b2 = DummyBlock(data=2)
    bd = BlockData(root)
    bd.append(b1)
    bd.append(b2)
    bd.remove(b1)
    assert root.next is b2
    assert b2.previous is root
    assert b1._container is None


def test_blockdata_of_type_with_mixed_types():
    root = DummyBlock(data=0)
    bd = BlockData(root)
    dummies = []
    for i in range(1, 6):
        d = DummyBlock(data=i)
        bd.append(d)
        bd.append(DefaultBlock(data=i))
        dummies.append(d)
    dummy_results = list(bd.of_type(DummyBlock))
    assert len(dummy_results) == 6
    assert dummy_results[0] is root
    for expected, actual in zip(dummies, dummy_results[1:], strict=False):
        assert actual is expected
    default_results = list(bd.of_type(DefaultBlock))
    assert len(default_results) == 5
    assert all(type(b) is DefaultBlock for b in default_results)


def test_blockdata_of_type_base_class():
    root = DummyBlock(data=0)
    bd = BlockData(root)
    for i in range(1, 6):
        bd.append(DummyBlock(data=i))
        bd.append(DefaultBlock(data=i))
    all_results = list(bd.of_type(Block))
    assert len(all_results) == 11
    items_from_iter = list(bd)
    assert all_results == items_from_iter


def test_blockdata_type_index_after_remove():
    root = DummyBlock(data=0)
    b1 = DummyBlock(data=1)
    b2 = DefaultBlock(data=2)
    bd = BlockData(root)
    bd.append(b1)
    bd.append(b2)
    bd.remove(b1)
    dummy_results = list(bd.of_type(DummyBlock))
    assert len(dummy_results) == 1
    assert dummy_results[0] is root
    default_results = list(bd.of_type(DefaultBlock))
    assert len(default_results) == 1
    assert default_results[0] is b2
    assert bd._type_index[DefaultBlock] == [1]


def test_blockdata_type_index_after_preppend():
    root = DummyBlock(data=0)
    bd = BlockData(root)
    bd.append(DefaultBlock(data=1))
    new = DummyBlock(data=2)
    bd.preppend(new)
    dummy_results = list(bd.of_type(DummyBlock))
    assert len(dummy_results) == 2
    assert dummy_results[0] is new
    assert dummy_results[1] is root
    assert bd._type_index[DummyBlock] == [0, 1]
    assert bd._type_index[DefaultBlock] == [2]
