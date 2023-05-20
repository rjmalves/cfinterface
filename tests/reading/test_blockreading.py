from typing import IO, List

from cfinterface.components.block import Block
from cfinterface.reading.blockreading import BlockReading

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


def test_blockreading_empty():
    filedata = ""
    br = BlockReading([DummyBlock])
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        bd = br.read("README.md", "utf-8")
        assert br.empty
        assert len(bd) == 1


def test_blockreading_withdata():
    data = "Hello, world!"
    filedata = (
        "\n".join([DummyBlock.BEGIN_PATTERN, data, DummyBlock.END_PATTERN])
        + "\n"
    )
    br = BlockReading([DummyBlock])
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        bd = br.read("README.md", "utf-8")
        assert not br.empty
        dbs = [b for b in bd.of_type(DummyBlock)]
        assert len(dbs) == 1
        assert dbs[0].data[0].strip() == DummyBlock.BEGIN_PATTERN
        assert dbs[0].data[1].strip() == data
        assert dbs[0].data[2].strip() == DummyBlock.END_PATTERN


def test_blockreading_withdata_frombuffer():
    data = "Hello, world!"
    filedata = (
        "\n".join([DummyBlock.BEGIN_PATTERN, data, DummyBlock.END_PATTERN])
        + "\n"
    )
    br = BlockReading([DummyBlock])
    bd = br.read(filedata, "utf-8")
    assert not br.empty
    dbs = [b for b in bd.of_type(DummyBlock)]
    assert len(dbs) == 1
    assert dbs[0].data[0].strip() == DummyBlock.BEGIN_PATTERN
    assert dbs[0].data[1].strip() == data
    assert dbs[0].data[2].strip() == DummyBlock.END_PATTERN
