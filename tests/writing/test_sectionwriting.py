from typing import IO, List

from cfinterface.components.section import Section
from cfinterface.data.sectiondata import SectionData
from cfinterface.writing.sectionwriting import SectionWriting

from tests.mocks.mock_open import mock_open
from io import StringIO
from unittest.mock import MagicMock, patch


class DummySection(Section):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data

    def read(self, file: IO) -> bool:
        self.data: List[str] = []
        line: str = file.readline()
        self.data.append(line)
        return True

    def write(self, file: IO) -> bool:
        file.write(self.data)
        return True


def test_sectionwriting_withdata():
    filedata = "Hello, World!"
    bd = SectionData(DummySection(data=filedata))
    bw = SectionWriting(bd)
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        bw.write("", "utf-8")
    m().write.assert_called_once_with(filedata)


def test_sectionwriting_withdata_tobuffer():
    filedata = "Hello, World!"
    bd = SectionData(DummySection(data=filedata))
    bw = SectionWriting(bd)
    m = StringIO("")
    bw.write(m, "utf-8")
    assert m.getvalue() == filedata
