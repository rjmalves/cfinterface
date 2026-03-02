import pytest

from cfinterface.components.field import Field
from cfinterface.components.literalfield import LiteralField


def test_default_field():
    field = Field(10, 20, value=1)
    assert field.value == 1


def test_default_field_read_error():
    with pytest.raises(NotImplementedError):
        field = Field(10, 20)
        field.read("")


def test_default_field_write_error():
    with pytest.raises(NotImplementedError):
        field = Field(10, 20, value=1)
        field.write("")


def test_field_has_no_class_level_T_typevar():
    # Field.T was a class-level TypeVar; it must no longer exist after moving
    # _T to module level.
    assert not hasattr(Field, "T")


def test_write_str_returns_str():
    field = LiteralField(size=5, starting_position=0, value="hello")
    result = field.write("")
    assert isinstance(result, str)


def test_write_bytes_returns_bytes():
    field = LiteralField(size=5, starting_position=0, value="hello")
    result = field.write(b"")
    assert isinstance(result, bytes)


def test_read_str_returns_value():
    field = LiteralField(size=5, starting_position=0)
    result = field.read("hello world")
    assert isinstance(result, str)


def test_read_bytes_returns_value():
    field = LiteralField(size=5, starting_position=0)
    result = field.read(b"hello world")
    assert isinstance(result, str)


def test_write_str_content_correct():
    field = LiteralField(size=5, starting_position=2, value="ABCDE")
    # line shorter than ending_position (7) — ljust padding applied
    result = field.write("  ")
    assert isinstance(result, str)
    assert len(result) >= 7
    assert result[2:7] == "ABCDE"


def test_write_bytes_content_correct():
    field = LiteralField(size=5, starting_position=2, value="ABCDE")
    # line shorter than ending_position (7) — ljust padding applied
    result = field.write(b"  ")
    assert isinstance(result, bytes)
    assert len(result) >= 7
    assert result[2:7] == b"ABCDE"
