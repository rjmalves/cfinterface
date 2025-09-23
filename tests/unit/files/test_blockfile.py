from typing import IO, List

from cfinterface.components.block import Block
from cfinterface.data.blockdata import BlockData
from cfinterface.files.blockfile import BlockFile

from tests.mocks.mock_open import mock_open
from io import StringIO
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
        self.data: List[str] = []
        while True:
            line: str = file.readline()
            self.data.append(line)
            if self.ends(line):
                break
        return True

    def write(self, file: IO) -> bool:
        for line in self.data:
            file.write(line)
        return True


class DummyBlockV2(Block):
    BEGIN_PATTERN = "bet"
    END_PATTERN = "ent"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data

    def read(self, file: IO) -> bool:
        self.data: List[str] = []
        while True:
            line: str = file.readline()
            self.data.append(line)
            if self.ends(line):
                break
        return True

    def write(self, file: IO) -> bool:
        for line in self.data:
            file.write(line)
        return True


class VersionedBlockFile(BlockFile):
    BLOCKS = [DummyBlockV2]
    VERSIONS = {"v1": [DummyBlock], "v2": [DummyBlockV2]}


def test_blockfile_eq():
    bf1 = BlockFile(data=BlockData(DummyBlock(data=-1)))
    bf2 = BlockFile(data=BlockData(DummyBlock(data=-1)))
    assert bf1 == bf2


def test_blockfile_not_eq_invalid_type():
    bf1 = BlockFile(data=BlockData(DummyBlock(data=-1)))
    bf2 = 5
    assert bf1 != bf2


def test_blockfile_not_eq_different_length():
    bd = BlockData(DummyBlock(data=-1))
    bd.append(DummyBlock(data=+1))
    bf1 = BlockFile(data=bd)
    bf2 = BlockFile(data=BlockData(DummyBlock(data=-1)))
    assert bf1 != bf2


def test_blockfile_not_eq_valid():
    bf1 = BlockFile(data=BlockData(DummyBlock(data=-1)))
    bf2 = BlockFile(data=BlockData(DummyBlock(data=+1)))
    assert bf1 != bf2


def test_blockfile_read():
    data = "Hello, world!"
    filedata = (
        "\n".join([DummyBlock.BEGIN_PATTERN, data, DummyBlock.END_PATTERN])
        + "\n"
    )
    BlockFile.BLOCKS = [DummyBlock]
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        f = BlockFile.read("README.md")
        assert len(f.data) == 2
        assert len(f.data.last.data) == 3
        assert f.data.last.data[1] == data + "\n"


def test_blockfile_read_frombuffer():
    data = "Hello, world!"
    filedata = (
        "\n".join([DummyBlock.BEGIN_PATTERN, data, DummyBlock.END_PATTERN])
        + "\n"
    )
    BlockFile.BLOCKS = [DummyBlock]
    f = BlockFile.read(filedata)
    assert len(f.data) == 2
    assert len(f.data.last.data) == 3
    assert f.data.last.data[1] == data + "\n"


def test_blockfile_write():
    data = "Hello, world!"
    bd = BlockData(DummyBlock(data=[data]))
    BlockFile.BLOCKS = [DummyBlock]
    f = BlockFile(bd)
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        f.write("")
    m().write.assert_called_once_with(data)


def test_blockfile_write_tobuffer():
    data = "Hello, world!"
    bd = BlockData(DummyBlock(data=[data]))
    BlockFile.BLOCKS = [DummyBlock]
    f = BlockFile(bd)
    m = StringIO()
    f.write(m)
    assert m.getvalue() == data


def test_blockfile_set_version():
    assert VersionedBlockFile.BLOCKS[0] == DummyBlockV2
    VersionedBlockFile.set_version("v1")
    assert VersionedBlockFile.BLOCKS[0] == DummyBlock
    VersionedBlockFile.set_version("v1.5")
    assert VersionedBlockFile.BLOCKS[0] == DummyBlock
    VersionedBlockFile.set_version("v2")
    assert VersionedBlockFile.BLOCKS[0] == DummyBlockV2
    VersionedBlockFile.set_version("v3")
    assert VersionedBlockFile.BLOCKS[0] == DummyBlockV2
    VersionedBlockFile.set_version("v0")
    assert VersionedBlockFile.BLOCKS[0] == DummyBlockV2
