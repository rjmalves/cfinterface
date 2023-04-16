from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.data.registerdata import RegisterData
from cfinterface.files.registerfile import RegisterFile

import pandas as pd  # type: ignore
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
