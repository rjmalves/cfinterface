import io

import pytest

from cfinterface.components.datetimefield import DatetimeField
from cfinterface.components.floatfield import FloatField
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.tabular import TabularParser


@pytest.fixture()
def integer_field_factory():
    def _factory(size=8, starting_position=0, value=None):
        return IntegerField(size, starting_position, value=value)

    return _factory


@pytest.fixture()
def float_field_factory():
    def _factory(
        size=8,
        starting_position=0,
        decimal_digits=4,
        format="F",
        sep=".",
        value=None,
    ):
        return FloatField(
            size,
            starting_position,
            decimal_digits,
            format=format,
            sep=sep,
            value=value,
        )

    return _factory


@pytest.fixture()
def literal_field_factory():
    def _factory(size=80, starting_position=0, value=None):
        return LiteralField(size, starting_position, value=value)

    return _factory


@pytest.fixture()
def datetime_field_factory():
    def _factory(size=16, starting_position=0, format="%Y/%m/%d", value=None):
        return DatetimeField(
            size, starting_position, format=format, value=value
        )

    return _factory


@pytest.fixture()
def tabular_parser_factory():
    def _factory(columns, delimiter=None):
        return TabularParser(columns, delimiter=delimiter)

    return _factory


@pytest.fixture()
def make_string_io():
    def _factory(lines):
        return io.StringIO("".join(lines))

    return _factory
