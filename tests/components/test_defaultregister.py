from cfinterface.components.defaultregister import DefaultRegister
from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


def test_default_register_eq():
    r1 = DefaultRegister(data=[0])
    r2 = DefaultRegister(data=[0])
    assert r1 == r2
    r1.data = [1]
    assert r1 != r2


def test_default_register_read():
    data = "Hello, world!\n"
    m: MagicMock = mock_open(read_data=data)
    with patch("builtins.open", m):
        with open("", "r") as fp:
            r = DefaultRegister()
            r.read_register(fp, storage="TEXT")
            assert r.data == data


def test_default_register_write():
    data = "Hello, world!\n"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "w") as fp:
            r = DefaultRegister()
            r.data = data
            r.write_register(fp)
    m().write.assert_called_once_with(data)
