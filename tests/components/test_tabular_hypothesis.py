"""Hypothesis property-based tests for TabularParser round-trips."""

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from cfinterface.components.floatfield import FloatField
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.tabular import ColumnDef, TabularParser


@st.composite
def integer_parser_with_data(
    draw: st.DrawFn,
) -> tuple[TabularParser, dict[str, list[int]]]:
    """Generate fixed-width integer-only TabularParser with matching data.

    1-4 columns of 8-char IntegerField with 1-10 rows of non-negative integers.
    """
    n_cols = draw(st.integers(min_value=1, max_value=4))
    col_size = 8  # fixed width per column
    columns = []
    for i in range(n_cols):
        name = f"col_{i}"
        field = IntegerField(col_size, i * col_size)
        columns.append(ColumnDef(name, field))
    parser = TabularParser(columns)
    n_rows = draw(st.integers(min_value=1, max_value=10))
    # Maximum positive value that fits in col_size textual characters
    max_val = 10**col_size - 1
    data: dict[str, list[int]] = {}
    for col in columns:
        data[col.name] = draw(
            st.lists(
                st.integers(min_value=0, max_value=max_val),
                min_size=n_rows,
                max_size=n_rows,
            )
        )
    return parser, data


@st.composite
def mixed_parser_with_data(
    draw: st.DrawFn,
) -> tuple[TabularParser, dict[str, list[object]]]:
    """Generate fixed-width mixed-type TabularParser with matching data.

    Layout: IntegerField(6, 0) + FloatField(10, 6, dec=2) + LiteralField(8, 16).
    Float values constrained to fit within 10-char field width; labels use L/N.
    """
    columns = [
        ColumnDef("id", IntegerField(6, 0)),
        ColumnDef("value", FloatField(10, 6, decimal_digits=2, format="F")),
        ColumnDef("label", LiteralField(8, 16)),
    ]
    parser = TabularParser(columns)
    n_rows = draw(st.integers(min_value=1, max_value=10))
    ids = draw(
        st.lists(
            st.integers(min_value=0, max_value=99999),
            min_size=n_rows,
            max_size=n_rows,
        )
    )
    values = draw(
        st.lists(
            st.floats(
                min_value=-999.0,
                max_value=9999.0,
                allow_nan=False,
                allow_infinity=False,
            ),
            min_size=n_rows,
            max_size=n_rows,
        )
    )
    labels = draw(
        st.lists(
            st.text(
                alphabet=st.characters(
                    whitelist_categories=("L", "N"),
                ),
                min_size=1,
                max_size=8,
            ),
            min_size=n_rows,
            max_size=n_rows,
        )
    )
    return parser, {"id": ids, "value": values, "label": labels}


@st.composite
def delimited_parser_with_data(
    draw: st.DrawFn,
) -> tuple[TabularParser, dict[str, list[int]]]:
    """Generate delimiter-separated IntegerField TabularParser with data.

    1-3 columns of IntegerField(8, 0) using common delimiters. LiteralField
    excluded to avoid ambiguity with unquoted fields.
    """
    delimiter = draw(st.sampled_from([";", ",", "\t"]))
    n_cols = draw(st.integers(min_value=1, max_value=3))
    columns = []
    for i in range(n_cols):
        columns.append(ColumnDef(f"col_{i}", IntegerField(8, 0)))
    parser = TabularParser(columns, delimiter=delimiter)
    n_rows = draw(st.integers(min_value=1, max_value=10))
    data: dict[str, list[int]] = {}
    for col in columns:
        data[col.name] = draw(
            st.lists(
                st.integers(min_value=0, max_value=9999999),
                min_size=n_rows,
                max_size=n_rows,
            )
        )
    return parser, data


@pytest.mark.slow
@settings(max_examples=200)
@given(args=integer_parser_with_data())
def test_integer_parser_roundtrip(
    args: tuple[TabularParser, dict[str, list[int]]],
) -> None:
    """Fixed-width integer parser: parse_lines(format_rows(data)) == data.

    For all integer columns in a fixed-width parser, formatting data to
    text lines and re-parsing must recover the original dict exactly.
    format_rows appends '\\n' to each line; it is stripped before re-parsing
    so that field character positions remain aligned.
    """
    parser, data = args
    formatted = parser.format_rows(data)
    reparsed = parser.parse_lines([ln.rstrip("\n") for ln in formatted])
    assert reparsed == data


@pytest.mark.slow
@settings(max_examples=200)
@given(args=mixed_parser_with_data())
def test_mixed_parser_roundtrip(
    args: tuple[TabularParser, dict[str, list[object]]],
) -> None:
    """Fixed-width mixed-type parser: round-trip with per-type tolerance.

    Integer and label columns must match exactly.  Float columns
    (decimal_digits=2) must match within 0.01 tolerance.

    Uses assume() to skip float values whose formatted representation at
    full decimal_digits=2 precision already overflows the 10-character
    field width; the writer reduces precision in that case and the
    effective tolerance would differ from 0.01.
    """
    parser, data = args
    values_list: list[float] = data["value"]  # type: ignore[assignment]
    for v in values_list:
        initial_formatted = f"{round(v, 2):.2F}"
        assume(len(initial_formatted) <= 10)
    formatted = parser.format_rows(data)
    reparsed = parser.parse_lines([ln.rstrip("\n") for ln in formatted])
    assert reparsed["id"] == data["id"]
    for v1, v2 in zip(reparsed["value"], data["value"], strict=False):  # type: ignore[arg-type]
        assert abs(v1 - v2) < 0.01  # type: ignore[operator]
    assert reparsed["label"] == data["label"]


@pytest.mark.slow
@settings(max_examples=200)
@given(args=delimited_parser_with_data())
def test_delimited_parser_roundtrip(
    args: tuple[TabularParser, dict[str, list[int]]],
) -> None:
    """Delimiter-separated integer parser: round-trip produces original data.

    format_rows appends '\\n' but __delimted_reading strips each token,
    so the trailing newline on the last token is removed during parsing —
    no explicit rstrip() is required before re-parsing.
    """
    parser, data = args
    formatted = parser.format_rows(data)
    reparsed = parser.parse_lines(formatted)
    assert reparsed == data
