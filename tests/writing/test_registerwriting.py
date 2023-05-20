from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.data.registerdata import RegisterData
from cfinterface.writing.registerwriting import RegisterWriting

from tests.mocks.mock_open import mock_open
from io import StringIO
from unittest.mock import MagicMock, patch


class DummyRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])


def test_registerwriting_withdata():
    filedata = "Hello, World!"
    bd = RegisterData(DummyRegister(data=[filedata]))
    bw = RegisterWriting(bd)
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        bw.write("", "utf-8")
    m().write.assert_called_once_with(
        DummyRegister.IDENTIFIER + " " + filedata + "\n"
    )


def test_registerwriting_withdata_tobuffer():
    filedata = "Hello, World!"
    bd = RegisterData(DummyRegister(data=[filedata]))
    bw = RegisterWriting(bd)
    m = StringIO("")
    bw.write(m, "utf-8")
    assert m.getvalue() == (DummyRegister.IDENTIFIER + " " + filedata + "\n")
