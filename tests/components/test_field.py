import pytest

from cfinterface.components.field import Field


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
