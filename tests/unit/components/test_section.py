from typing import IO

import pytest
from cfinterface.components.literalfield import LiteralField

from cfinterface.components.section import Section
from tests.mocks.mock_open import mock_open

from unittest.mock import MagicMock, patch


class DummySection(Section):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data

    def read(self, file: IO) -> bool:
        self.data = file.readline().strip()
        return True

    def write(self, file: IO) -> bool:
        file.write(self.data)
        return True


class DummyBinarySection(Section):
    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)
        self._field = LiteralField(5)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data

    def read(self, file: IO) -> bool:
        self._field.read(file.read(self._field.size))
        self.data = self._field.value
        return True

    def write(self, file: IO) -> bool:
        self._field.value = self.data
        file.write(self._field.write(b""))
        return True


def test_single_section_properties():
    s1 = Section()
    assert s1.is_first
    assert s1.is_last


def test_section_simple_chain_properties():
    # Build a simple section chain
    s1 = Section()
    s2 = Section()
    s3 = Section()
    # Sets relationships
    s1.next = s2
    s2.previous = s1
    s2.next = s3
    s3.previous = s2
    # Asserts properties
    assert s1.is_first
    assert s3.is_last
    assert not s1.is_last
    assert not s2.is_first
    assert not s2.is_last
    assert not s3.is_first
    assert s1.empty
    assert s2.empty
    assert s3.empty


def test_section_equal_error():
    s1 = Section()
    s2 = Section()
    with pytest.raises(NotImplementedError):
        s1 == s2


def test_section_read_error():
    s = Section()
    with pytest.raises(NotImplementedError):
        m: MagicMock = mock_open(read_data="")
        with patch("builtins.open", m):
            with open("", "r") as fp:
                s.read_section(fp)


def test_section_write_error():
    s = Section()
    with pytest.raises(NotImplementedError):
        m: MagicMock = mock_open(read_data="")
        with patch("builtins.open", m):
            with open("", "r") as fp:
                s.write_section(fp)


def test_dummy_section_equal():
    s1 = DummySection()
    s2 = DummySection()
    assert s1 == s2


def test_dummy_section_read():
    data = "Hello, world!"
    m: MagicMock = mock_open(read_data=data)
    with patch("builtins.open", m):
        with open("", "r") as fp:
            s = DummySection()
            s.read_section(fp)
            assert s.data == data


def test_dummy_section_write():
    data = "Hello, world!"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "w") as fp:
            b = DummySection()
            b.data = data
            b.write_section(fp)
    m().write.assert_called_once_with(data)


def test_dummy_binarysection_read():
    data = "hello"
    filedata = b"hello"
    m: MagicMock = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "rb") as fp:
            s = DummyBinarySection()
            s.read_section(fp)
            assert s.data == data


def test_dummy_binarysection_write():
    data = "hello"
    filedata = ""
    m = mock_open(read_data=filedata)
    with patch("builtins.open", m):
        with open("", "wb") as fp:
            b = DummyBinarySection()
            b.data = data
            b.write_section(fp)
    m().write.assert_called_once_with(b"hello")
