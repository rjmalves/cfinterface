from typing import IO, List

from cfinterface.components.section import Section
from cfinterface.reading.sectionreading import SectionReading

from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


class DummySection(Section):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data

    def read(self, file: IO) -> bool:
        self.data: List[str] = []
        self.data.append(file.readline())
        return True

    def write(self, file: IO) -> bool:
        for line in self.data:
            file.write(line)
        return True


def test_sectionreading_withdata():
    data = "Hello, world!"
    sr = SectionReading([DummySection])
    m: MagicMock = mock_open(read_data=data + "\n")
    with patch("builtins.open", m):
        sd = sr.read("", "")
        assert not sr.empty
        dbs = [b for b in sd.of_type(DummySection)]
        assert len(dbs) == 1
        assert dbs[0].data[0].strip() == data
