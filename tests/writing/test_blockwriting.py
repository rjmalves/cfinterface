from typing import IO, List

from cfinterface.components.block import Block
from cfinterface.data.blockdata import BlockData
from cfinterface.writing.blockwriting import BlockWriting

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
        file.write(self.data)
        return True


def test_blockwriting_withdata():
    filedata = "Hello, World!"
    bd = BlockData(DummyBlock(data=filedata))
    bw = BlockWriting(bd)
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        bw.write("./test.txt", "utf-8")
    m().write.assert_called_once_with(filedata)


def test_blockwriting_withdata_tobuffer():
    filedata = "Hello, World!"
    bd = BlockData(DummyBlock(data=filedata))
    bw = BlockWriting(bd)
    m = StringIO("")
    bw.write(m, "utf-8")
    assert m.getvalue() == filedata
