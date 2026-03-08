import warnings
from io import StringIO
from typing import IO
from unittest.mock import MagicMock, patch

import pytest

from cfinterface.components.section import Section
from cfinterface.data.sectiondata import SectionData
from cfinterface.files.sectionfile import SectionFile
from tests.mocks.mock_open import mock_open


class DummySection(Section):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return o.data == self.data

    def read(self, file: IO) -> bool:
        self.data: list[str] = []
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
        return o.data == self.data

    def read(self, file: IO) -> bool:
        self.data: list[str] = []
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
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
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


def test_sectionfile_read_with_version():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySectionV2]
    f = VersionedSectionFile.read(data + "\n", version="v1")
    assert len(f.data.last.data) == 1
    assert f.data.last.data[0] == data + "\n"
    assert VersionedSectionFile.SECTIONS[0] == DummySectionV2


def test_sectionfile_read_version_below_all():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySectionV2]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        VersionedSectionFile.read(data + "\n", version="v0")
        assert len(w) == 1
        assert "No matching version" in str(w[0].message)


def test_sectionfile_read_version_above_all():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySectionV2]
    f = VersionedSectionFile.read(data + "\n", version="v3")
    assert len(f.data.last.data) == 1
    assert f.data.last.data[0] == data + "\n"


def test_sectionfile_read_no_version():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySectionV2]
    f = VersionedSectionFile.read(data + "\n")
    assert len(f.data.last.data) == 1
    assert f.data.last.data[0] == data + "\n"


def test_sectionfile_set_version_deprecation():
    with pytest.warns(DeprecationWarning, match="set_version.*deprecated"):
        VersionedSectionFile.set_version("v1")
    assert VersionedSectionFile.SECTIONS[0] == DummySection


def test_sectionfile_set_version_still_mutates():
    VersionedSectionFile.SECTIONS = [DummySectionV2]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        VersionedSectionFile.set_version("v1")
    assert VersionedSectionFile.SECTIONS[0] == DummySection


def test_sectionfile_read_many():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySection]
    m: MagicMock = mock_open(read_data=data + "\n")
    with patch("builtins.open", m):
        result = VersionedSectionFile.read_many(["README.md", "pyproject.toml"])
    assert len(result) == 2
    assert isinstance(result["README.md"], VersionedSectionFile)


def test_sectionfile_read_many_empty():
    result = VersionedSectionFile.read_many([])
    assert result == {}


def test_sectionfile_read_many_with_version():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySectionV2]
    m: MagicMock = mock_open(read_data=data + "\n")
    with patch("builtins.open", m):
        result = VersionedSectionFile.read_many(["README.md"], version="v1")
    assert len(result) == 1
    assert VersionedSectionFile.SECTIONS[0] == DummySectionV2


def test_sectionfile_read_many_no_class_mutation():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySectionV2]
    m: MagicMock = mock_open(read_data=data + "\n")
    with patch("builtins.open", m):
        VersionedSectionFile.read_many(["README.md"], version="v1")
    assert VersionedSectionFile.SECTIONS[0] == DummySectionV2


from cfinterface.versioning import VersionMatchResult  # noqa: E402


def test_sectionfile_validate_matched():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySection]
    f = VersionedSectionFile.read(data + "\n", version="v1")
    result = f.validate(version="v1")
    assert isinstance(result, VersionMatchResult)
    assert DummySection in result.found_types


def test_sectionfile_validate_no_version():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySection]
    f = VersionedSectionFile.read(data + "\n")
    result = f.validate()
    assert isinstance(result, VersionMatchResult)


def test_sectionfile_validate_unknown_version():
    data = "Hello, world!"
    VersionedSectionFile.SECTIONS = [DummySection]
    f = VersionedSectionFile.read(data + "\n")
    result = f.validate(version="v0")
    assert result.matched is False
