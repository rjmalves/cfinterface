from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.reading.registerreading import RegisterReading

from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


class DummyRegister(Register):
    IDENTIFIER = "reg"
    IDENTIFIER_DIGITS = 4
    LINE = Line([LiteralField(13, 4)])


def test_registerreading_empty():
    filedata = ""
    br = RegisterReading([DummyRegister])
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        bd = br.read("", "")
        assert br.empty
        assert len(bd) == 1


def test_registerreading_withdata():
    data = "Hello, world!"
    br = RegisterReading([DummyRegister])
    m: MagicMock = mock_open(
        read_data=DummyRegister.IDENTIFIER + " " + data + "\n"
    )
    with patch("builtins.open", m):
        bd = br.read("", "")
        assert not br.empty
        dbs = [b for b in bd.of_type(DummyRegister)]
        assert len(dbs) == 1
        assert dbs[0].data[0].strip() == data
