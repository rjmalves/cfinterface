from typing import IO, List

from cfinterface.components.section import Section
from cfinterface.data.sectiondata import SectionData
from cfinterface.files.sectionfile import SectionFile

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
        for line in self.data:
            file.write(line)
        return True


class DummySectionV2(Section):
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
        for line in self.data:
            file.write(line)
        return True


class VersionedSectionFile(SectionFile):
    SECTIONS = [DummySectionV2]
    VERSIONS = {"v1": [DummySection], "v2": [DummySectionV2]}


def test_sectionfile_eq():
    bf1 = SectionFile(data=SectionData(DummySection(data=-1)))
    bf2 = SectionFile(data=SectionData(DummySection(data=-1)))
    assert bf1 == bf2


def test_sectionfile_not_eq_invalid_type():
    bf1 = SectionFile(data=SectionData(DummySection(data=-1)))
    bf2 = 5
    assert bf1 != bf2


def test_sectionfile_not_eq_different_length():
    bd = SectionData(DummySection(data=-1))
    bd.append(DummySection(data=+1))
    bf1 = SectionFile(data=bd)
    bf2 = SectionFile(data=SectionData(DummySection(data=-1)))
    assert bf1 != bf2


def test_sectionfile_not_eq_valid():
    bf1 = SectionFile(data=SectionData(DummySection(data=-1)))
    bf2 = SectionFile(data=SectionData(DummySection(data=+1)))
    assert bf1 != bf2


def test_sectionfile_read():
    data = "Hello, world!"
    SectionFile.SECTIONS = [DummySection]
    m: MagicMock = mock_open(read_data=data + "\n")
    with patch("builtins.open", m):
        f = SectionFile.read("README.md")
        assert len(f.data) == 2
        assert len(f.data.last.data) == 1
        assert f.data.last.data[0] == data + "\n"


def test_sectionfile_read_frombuffer():
    data = "Hello, world!"
    SectionFile.SECTIONS = [DummySection]
    f = SectionFile.read(data + "\n")
    assert len(f.data) == 2
    assert len(f.data.last.data) == 1
    assert f.data.last.data[0] == data + "\n"


def test_sectionfile_write():
    data = "Hello, world!"
    bd = SectionData(DummySection(data=[data]))
    SectionFile.SECTIONS = [DummySection]
    f = SectionFile(bd)
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        f.write("")
    m().write.assert_called_once_with(data)


def test_sectionfile_write_tobuffer():
    data = "Hello, world!"
    bd = SectionData(DummySection(data=[data]))
    SectionFile.SECTIONS = [DummySection]
    f = SectionFile(bd)
    m = StringIO()
    f.write(m)
    m.getvalue() == data


def test_sectionfile_set_version():
    assert VersionedSectionFile.SECTIONS[0] == DummySectionV2
    VersionedSectionFile.set_version("v1")
    assert VersionedSectionFile.SECTIONS[0] == DummySection
    VersionedSectionFile.set_version("v1.5")
    assert VersionedSectionFile.SECTIONS[0] == DummySection
    VersionedSectionFile.set_version("v2")
    assert VersionedSectionFile.SECTIONS[0] == DummySectionV2
    VersionedSectionFile.set_version("v3")
    assert VersionedSectionFile.SECTIONS[0] == DummySectionV2
    VersionedSectionFile.set_version("v0")
    assert VersionedSectionFile.SECTIONS[0] == DummySectionV2
