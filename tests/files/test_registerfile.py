import warnings

import pandas as pd  # type: ignore
import pytest

from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.data.registerdata import RegisterData
from cfinterface.files.registerfile import RegisterFile
from tests.mocks.mock_open import mock_open
from io import StringIO
from unittest.mock import MagicMock, patch


class DummyRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])

    @property
    def my_prop(self) -> str:
        return self.data


class DummyRegisterV2(Register):
    IDENTIFIER = "ret"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])

    @property
    def my_prop(self) -> str:
        return self.data


class VersionedRegisterFile(RegisterFile):
    REGISTERS = [DummyRegisterV2]
    VERSIONS = {"v1": [DummyRegister], "v2": [DummyRegisterV2]}


def test_registerfile_eq():
    rf1 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    rf2 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    assert rf1 == rf2


def test_registerfile_not_eq_invalid_type():
    rf1 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    rf2 = 5
    assert rf1 != rf2


def test_registerfile_not_eq_different_length():
    bd = RegisterData(DummyRegister(data=-1))
    bd.append(DummyRegister(data=+1))
    rf1 = RegisterFile(data=bd)
    rf2 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    assert rf1 != rf2


def test_registerfile_as_df():
    rf = RegisterFile(data=RegisterData(DummyRegister(data="testing")))
    df = rf._as_df(DummyRegister)
    assert isinstance(df, pd.DataFrame)
    assert df.at[0, "my_prop"] == "testing"


def test_registerfile_not_eq_valid():
    rf1 = RegisterFile(data=RegisterData(DummyRegister(data=-1)))
    rf2 = RegisterFile(data=RegisterData(DummyRegister(data=+1)))
    assert rf1 != rf2


def test_registerfile_as_df_empty():
    rf = RegisterFile()
    result = rf._as_df(Register)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_registerfile_read():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    RegisterFile.REGISTERS = [DummyRegister]
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        f = RegisterFile.read("README.md")
        assert len(f.data) == 2
        assert f.data.last.data[0] == data


def test_registerfile_read_frombuffer():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    RegisterFile.REGISTERS = [DummyRegister]
    f = RegisterFile.read(filedata)
    assert len(f.data) == 2
    assert f.data.last.data[0] == data


def test_registerfile_write():
    data = "Hello, world!"
    bd = RegisterData(DummyRegister(data=[data]))
    RegisterFile.REGISTERS = [DummyRegister]
    f = RegisterFile(bd)
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        f.write("")
    m().write.assert_called_once_with(
        DummyRegister.IDENTIFIER + " " + data + "\n"
    )


def test_registerfile_write_tobuffer():
    data = "Hello, world!"
    bd = RegisterData(DummyRegister(data=[data]))
    RegisterFile.REGISTERS = [DummyRegister]
    f = RegisterFile(bd)
    m = StringIO()
    f.write(m)
    m.getvalue() == DummyRegister.IDENTIFIER + " " + data + "\n"


def test_registerfile_set_version():
    assert VersionedRegisterFile.REGISTERS[0] == DummyRegisterV2
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        VersionedRegisterFile.set_version("v1")
        assert VersionedRegisterFile.REGISTERS[0] == DummyRegister
        VersionedRegisterFile.set_version("v1.5")
        assert VersionedRegisterFile.REGISTERS[0] == DummyRegister
        VersionedRegisterFile.set_version("v2")
        assert VersionedRegisterFile.REGISTERS[0] == DummyRegisterV2
        VersionedRegisterFile.set_version("v3")
        assert VersionedRegisterFile.REGISTERS[0] == DummyRegisterV2
        VersionedRegisterFile.set_version("v0")
        assert VersionedRegisterFile.REGISTERS[0] == DummyRegisterV2


def test_registerfile_read_with_version():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegisterV2]
    f = VersionedRegisterFile.read(filedata, version="v1")
    assert f.data.last.data[0] == data
    assert VersionedRegisterFile.REGISTERS[0] == DummyRegisterV2


def test_registerfile_read_version_above_all():
    data = "Hello, world!"
    filedata = DummyRegisterV2.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegisterV2]
    f = VersionedRegisterFile.read(filedata, version="v3")
    assert f.data.last.data[0] == data


def test_registerfile_read_version_below_all():
    data = "Hello, world!"
    filedata = DummyRegisterV2.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegisterV2]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        f = VersionedRegisterFile.read(filedata, version="v0")
        assert len(w) == 1
        assert "No matching version" in str(w[0].message)
    assert f.data.last.data[0] == data


def test_registerfile_read_no_version():
    data = "Hello, world!"
    filedata = DummyRegisterV2.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegisterV2]
    f = VersionedRegisterFile.read(filedata)
    assert f.data.last.data[0] == data


def test_registerfile_set_version_deprecation():
    with pytest.warns(DeprecationWarning, match="set_version.*deprecated"):
        VersionedRegisterFile.set_version("v1")
    assert VersionedRegisterFile.REGISTERS[0] == DummyRegister


def test_registerfile_set_version_still_mutates():
    VersionedRegisterFile.REGISTERS = [DummyRegisterV2]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        VersionedRegisterFile.set_version("v1")
    assert VersionedRegisterFile.REGISTERS[0] == DummyRegister


def test_registerfile_read_many():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegister]
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        result = VersionedRegisterFile.read_many(
            ["README.md", "pyproject.toml"]
        )
    assert len(result) == 2
    assert "README.md" in result
    assert "pyproject.toml" in result
    assert isinstance(result["README.md"], VersionedRegisterFile)


def test_registerfile_read_many_empty():
    result = VersionedRegisterFile.read_many([])
    assert result == {}


def test_registerfile_read_many_with_version():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegisterV2]
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        result = VersionedRegisterFile.read_many(["README.md"], version="v1")
    assert len(result) == 1
    assert result["README.md"].data.last.data[0] == data
    assert VersionedRegisterFile.REGISTERS[0] == DummyRegisterV2


def test_registerfile_read_many_no_class_mutation():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegisterV2]
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        VersionedRegisterFile.read_many(["README.md"], version="v1")
    assert VersionedRegisterFile.REGISTERS[0] == DummyRegisterV2


from cfinterface.versioning import VersionMatchResult  # noqa: E402


def test_registerfile_validate_matched():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegister]
    f = VersionedRegisterFile.read(filedata, version="v1")
    result = f.validate(version="v1")
    assert isinstance(result, VersionMatchResult)
    assert DummyRegister in result.found_types


def test_registerfile_validate_no_version():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegister]
    f = VersionedRegisterFile.read(filedata)
    result = f.validate()
    assert isinstance(result, VersionMatchResult)


def test_registerfile_validate_unknown_version():
    data = "Hello, world!"
    filedata = DummyRegister.IDENTIFIER + " " + data + "\n"
    VersionedRegisterFile.REGISTERS = [DummyRegister]
    f = VersionedRegisterFile.read(filedata)
    result = f.validate(version="v0")
    assert result.matched is False
