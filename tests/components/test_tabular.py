"""Tests for cfinterface.components.tabular — TabularParser, ColumnDef, TabularSection."""

import io
from unittest.mock import patch

import pytest

from cfinterface.components.floatfield import FloatField
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.tabular import (
    ColumnDef,
    TabularParser,
    TabularSection,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_integer_parser() -> TabularParser:
    cols = [
        ColumnDef("a", IntegerField(4, 0)),
        ColumnDef("b", IntegerField(4, 4)),
    ]
    return TabularParser(cols)


def _make_mixed_parser() -> TabularParser:
    cols = [
        ColumnDef("id", IntegerField(4, 0)),
        ColumnDef("value", FloatField(8, 4, decimal_digits=2)),
        ColumnDef("label", LiteralField(6, 12)),
    ]
    return TabularParser(cols)


# ---------------------------------------------------------------------------
# 1. ColumnDef structure
# ---------------------------------------------------------------------------


def test_columndef_creation() -> None:
    """ColumnDef is a named tuple with name and field attributes."""
    field = IntegerField(4, 0)
    col = ColumnDef("my_col", field)
    assert col.name == "my_col"
    assert col.field is field


def test_columndef_is_namedtuple() -> None:
    """ColumnDef instances support tuple indexing and unpacking."""
    field = LiteralField(10, 0)
    col = ColumnDef("txt", field)
    name, f = col  # unpacking
    assert name == "txt"
    assert f is field
    assert col[0] == "txt"
    assert col[1] is field


# ---------------------------------------------------------------------------
# 2. parse_lines — integer columns
# ---------------------------------------------------------------------------


def test_parse_lines_integer_columns() -> None:
    """Parse 3 lines with 2 IntegerField columns; verify types and values."""
    parser = _make_integer_parser()
    lines = ["   1   2", "   3   4", "   5   6"]
    result = parser.parse_lines(lines)
    assert list(result.keys()) == ["a", "b"]
    assert result["a"] == [1, 3, 5]
    assert result["b"] == [2, 4, 6]


def test_parse_lines_single_column() -> None:
    """Edge case: parser with a single column returns a single-key dict."""
    cols = [ColumnDef("num", IntegerField(5, 0))]
    parser = TabularParser(cols)
    lines = ["   42", "  100", "    7"]
    result = parser.parse_lines(lines)
    assert list(result.keys()) == ["num"]
    assert result["num"] == [42, 100, 7]


# ---------------------------------------------------------------------------
# 3. parse_lines — mixed field types
# ---------------------------------------------------------------------------


def test_parse_lines_mixed_columns() -> None:
    """Parse lines with IntegerField, FloatField, LiteralField columns."""
    parser = _make_mixed_parser()
    # width: id=4, value=8, label=6 → total 18 chars per line
    lines = [
        "   1    1.25hello ",
        "   2    2.50world ",
    ]
    result = parser.parse_lines(lines)
    assert list(result.keys()) == ["id", "value", "label"]
    assert result["id"] == [1, 2]
    assert abs(result["value"][0] - 1.25) < 1e-6
    assert abs(result["value"][1] - 2.50) < 1e-6
    assert result["label"] == ["hello", "world"]


# ---------------------------------------------------------------------------
# 4. parse_lines — empty input
# ---------------------------------------------------------------------------


def test_parse_lines_empty_input() -> None:
    """parse_lines([]) returns a dict with correct keys mapping to empty lists."""
    parser = _make_integer_parser()
    result = parser.parse_lines([])
    assert list(result.keys()) == ["a", "b"]
    assert result["a"] == []
    assert result["b"] == []


def test_parse_lines_empty_input_preserves_column_count() -> None:
    """Empty parse on a 3-column parser still yields 3 keys."""
    parser = _make_mixed_parser()
    result = parser.parse_lines([])
    assert len(result) == 3


# ---------------------------------------------------------------------------
# 5. parse_lines — malformed row
# ---------------------------------------------------------------------------


def test_parse_lines_malformed_row_filled_with_none() -> None:
    """A line that cannot be read produces None for every column in that row."""
    parser = _make_integer_parser()
    # An alphabetic line triggers ValueError inside IntegerField._textual_read
    lines = ["   1   2", "BADLINE!", "   5   6"]
    result = parser.parse_lines(lines)
    # Good rows parsed correctly
    assert result["a"][0] == 1
    assert result["b"][0] == 2
    assert result["a"][2] == 5
    assert result["b"][2] == 6
    # Malformed row filled with None
    assert result["a"][1] is None
    assert result["b"][1] is None


def test_parse_lines_malformed_row_count_preserved() -> None:
    """Row count equals number of input lines even when a row is malformed."""
    parser = _make_integer_parser()
    lines = ["   1   2", "BADLINE!", "   5   6"]
    result = parser.parse_lines(lines)
    assert len(result["a"]) == 3
    assert len(result["b"]) == 3


# ---------------------------------------------------------------------------
# 6. format_rows — basic
# ---------------------------------------------------------------------------


def test_format_rows_basic() -> None:
    """format_rows produces one line per row with trailing newline."""
    parser = _make_integer_parser()
    data = {"a": [1, 3], "b": [2, 4]}
    lines = parser.format_rows(data)
    assert len(lines) == 2
    # Line.write() always appends \n
    for line in lines:
        assert line.endswith("\n")


def test_format_rows_empty_data() -> None:
    """format_rows on empty lists produces an empty list of lines."""
    parser = _make_integer_parser()
    data = {"a": [], "b": []}
    lines = parser.format_rows(data)
    assert lines == []


# ---------------------------------------------------------------------------
# 7. Round-trip: parse → format → re-parse
# ---------------------------------------------------------------------------


def test_round_trip_integer_columns() -> None:
    """Round-trip: parse → format → re-parse reproduces equivalent integer data."""
    parser = _make_integer_parser()
    original_lines = ["   1   2", "   3   4", "   5   6"]
    parsed = parser.parse_lines(original_lines)
    formatted = parser.format_rows(parsed)
    # Strip trailing \n before re-parsing so field positions still match
    reparsed = parser.parse_lines([ln.rstrip("\n") for ln in formatted])
    assert reparsed["a"] == parsed["a"]
    assert reparsed["b"] == parsed["b"]


def test_round_trip_mixed_columns() -> None:
    """Round-trip with mixed field types reproduces equivalent data."""
    parser = _make_mixed_parser()
    lines = [
        "   1    1.25hello ",
        "   2    2.50world ",
        "   3    0.00foo   ",
    ]
    parsed = parser.parse_lines(lines)
    formatted = parser.format_rows(parsed)
    reparsed = parser.parse_lines([ln.rstrip("\n") for ln in formatted])
    assert reparsed["id"] == parsed["id"]
    for v1, v2 in zip(reparsed["value"], parsed["value"]):
        assert abs(v1 - v2) < 1e-4
    assert reparsed["label"] == parsed["label"]


# ---------------------------------------------------------------------------
# 8. to_dataframe
# ---------------------------------------------------------------------------


def test_to_dataframe_basic() -> None:
    """to_dataframe() returns a DataFrame with correct columns and data."""
    pytest.importorskip("pandas")
    data = {"a": [1, 3, 5], "b": [2, 4, 6]}
    df = TabularParser.to_dataframe(data)
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 3
    assert df["a"].tolist() == [1, 3, 5]
    assert df["b"].tolist() == [2, 4, 6]


def test_to_dataframe_import_error() -> None:
    """to_dataframe() raises ImportError with install instructions when pandas absent."""
    with patch.dict("sys.modules", {"pandas": None}):
        with pytest.raises(ImportError) as exc_info:
            TabularParser.to_dataframe({"a": [1]})
    assert "pip install cfinterface[pandas]" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 9. Import / re-export
# ---------------------------------------------------------------------------


def test_tabularparser_importable_from_module() -> None:
    """TabularParser and ColumnDef are importable from cfinterface.components.tabular."""
    from cfinterface.components.tabular import ColumnDef as CD
    from cfinterface.components.tabular import TabularParser as TP

    assert TP is TabularParser
    assert CD is ColumnDef


def test_tabularparser_reexported_from_components() -> None:
    """TabularParser and ColumnDef are re-exported from cfinterface.components."""
    from cfinterface.components import ColumnDef as CD
    from cfinterface.components import TabularParser as TP

    assert TP is TabularParser
    assert CD is ColumnDef


# ---------------------------------------------------------------------------
# 10. column_names property / slot check
# ---------------------------------------------------------------------------


def test_parser_column_names_accessible_via_columns() -> None:
    """Column names can be retrieved from the parser's _columns attribute."""
    cols = [
        ColumnDef("x", IntegerField(4, 0)),
        ColumnDef("y", IntegerField(4, 4)),
        ColumnDef("z", IntegerField(4, 8)),
    ]
    parser = TabularParser(cols)
    names = [col.name for col in parser._columns]
    assert names == ["x", "y", "z"]


def test_parser_uses_slots() -> None:
    """TabularParser must not have a __dict__ (uses __slots__)."""
    parser = _make_integer_parser()
    assert not hasattr(parser, "__dict__")


def test_parse_lines_five_lines_three_columns() -> None:
    """Given 3 columns and 5 valid lines the result has 3 keys each of length 5."""
    parser = _make_mixed_parser()
    lines = [
        "   1    1.00alpha ",
        "   2    2.00beta  ",
        "   3    3.00gamma ",
        "   4    4.00delta ",
        "   5    5.00epsil ",
    ]
    result = parser.parse_lines(lines)
    assert len(result) == 3
    for key in ("id", "value", "label"):
        assert len(result[key]) == 5


# ---------------------------------------------------------------------------
# Helpers for TabularSection tests
# ---------------------------------------------------------------------------


class _YearValueSection(TabularSection):
    """Minimal subclass: 2 columns, 1 header line, no end pattern."""

    COLUMNS = [
        ColumnDef("year", IntegerField(4, 0)),
        ColumnDef("value", FloatField(8, 4, 2)),
    ]
    HEADER_LINES = 1
    END_PATTERN = ""


class _TwoHeaderSection(TabularSection):
    """Subclass with 2 header lines to test multi-header preservation."""

    COLUMNS = [
        ColumnDef("a", IntegerField(4, 0)),
        ColumnDef("b", IntegerField(4, 4)),
    ]
    HEADER_LINES = 2
    END_PATTERN = ""


class _EndPatternSection(TabularSection):
    """Subclass that stops reading at a line matching 'TOTAL'."""

    COLUMNS = [
        ColumnDef("a", IntegerField(4, 0)),
        ColumnDef("b", IntegerField(4, 4)),
    ]
    HEADER_LINES = 0
    END_PATTERN = "TOTAL"


def _build_file(lines: list) -> io.StringIO:
    return io.StringIO("".join(lines))


# ---------------------------------------------------------------------------
# 11. TabularSection.read — basic
# ---------------------------------------------------------------------------


def test_tabular_section_read_basic() -> None:
    """1 header + 3 data lines + blank line: data has 2 keys each with 3 elements."""
    content = [
        "HEADER LINE\n",
        "2001    1.25\n",
        "2002    2.50\n",
        "2003    3.75\n",
        "\n",
    ]
    sec = _YearValueSection()
    sec.read(_build_file(content))
    assert sec.data is not None
    assert list(sec.data.keys()) == ["year", "value"]
    assert sec.data["year"] == [2001, 2002, 2003]
    assert len(sec.data["value"]) == 3
    assert abs(sec.data["value"][0] - 1.25) < 1e-6
    assert abs(sec.data["value"][1] - 2.50) < 1e-6
    assert abs(sec.data["value"][2] - 3.75) < 1e-6


# ---------------------------------------------------------------------------
# 12. TabularSection.write — basic
# ---------------------------------------------------------------------------


def test_tabular_section_write_basic() -> None:
    """write() produces the header line followed by the correctly formatted rows."""
    content = [
        "MY HEADER\n",
        "2001    1.25\n",
        "2002    2.50\n",
        "\n",
    ]
    sec = _YearValueSection()
    sec.read(_build_file(content))

    out = io.StringIO()
    sec.write(out)
    written = out.getvalue()

    assert written.startswith("MY HEADER\n")
    assert "2001" in written
    assert "2002" in written


# ---------------------------------------------------------------------------
# 13. TabularSection round-trip
# ---------------------------------------------------------------------------


def test_tabular_section_round_trip() -> None:
    """read then write produces output that re-parses to the same data."""
    content = [
        "HEADER\n",
        "2001    1.25\n",
        "2002    2.50\n",
        "2003    3.75\n",
        "\n",
    ]
    sec = _YearValueSection()
    sec.read(_build_file(content))

    out = io.StringIO()
    sec.write(out)
    written = out.getvalue()

    sec2 = _YearValueSection()
    sec2.read(io.StringIO(written))

    assert sec2.data is not None
    assert sec2.data["year"] == sec.data["year"]
    for v1, v2 in zip(sec2.data["value"], sec.data["value"]):
        assert abs(v1 - v2) < 1e-4


# ---------------------------------------------------------------------------
# 14. TabularSection end pattern
# ---------------------------------------------------------------------------


def test_tabular_section_end_pattern() -> None:
    """END_PATTERN stops reading and file pointer is rewound to matching line."""
    content = [
        "   1   2\n",
        "   3   4\n",
        "TOTAL  6\n",
        "   7   8\n",
    ]
    f = _build_file(content)
    sec = _EndPatternSection()
    sec.read(f)

    # Only two data rows before TOTAL
    assert sec.data is not None
    assert sec.data["a"] == [1, 3]
    assert sec.data["b"] == [2, 4]

    # File pointer rewound: next readline() returns the TOTAL line
    next_line = f.readline()
    assert "TOTAL" in next_line


# ---------------------------------------------------------------------------
# 15. TabularSection empty data after headers
# ---------------------------------------------------------------------------


def test_tabular_section_empty_data() -> None:
    """File with only headers + blank line: data is empty dict-of-lists with correct keys."""
    content = [
        "HEADER\n",
        "\n",
    ]
    sec = _YearValueSection()
    sec.read(_build_file(content))

    assert sec.data is not None
    assert list(sec.data.keys()) == ["year", "value"]
    assert sec.data["year"] == []
    assert sec.data["value"] == []


# ---------------------------------------------------------------------------
# 16. TabularSection write when data is None
# ---------------------------------------------------------------------------


def test_tabular_section_write_none_data() -> None:
    """write() with data=None writes only headers and does not crash."""
    # Force _headers to a known value without calling read()
    sec = _YearValueSection()
    sec._headers = ["MY HEADER\n"]

    out = io.StringIO()
    result = sec.write(out)

    assert result is True
    assert out.getvalue() == "MY HEADER\n"


# ---------------------------------------------------------------------------
# 17. TabularSection header preservation
# ---------------------------------------------------------------------------


def test_tabular_section_header_preservation() -> None:
    """Two header lines are preserved exactly through a read/write cycle."""
    content = [
        "FIRST HEADER\n",
        "SECOND HEADER\n",
        "   1   2\n",
        "   3   4\n",
        "\n",
    ]
    sec = _TwoHeaderSection()
    sec.read(_build_file(content))

    out = io.StringIO()
    sec.write(out)
    written = out.getvalue()

    assert written.startswith("FIRST HEADER\nSECOND HEADER\n")


# ---------------------------------------------------------------------------
# 18. TabularSection __eq__
# ---------------------------------------------------------------------------


def test_tabular_section_equality() -> None:
    """Instances with same class and same data are equal; mismatches are not."""
    content = [
        "HDR\n",
        "2001    1.25\n",
        "\n",
    ]
    sec_a = _YearValueSection()
    sec_a.read(_build_file(content))

    sec_b = _YearValueSection()
    sec_b.read(_build_file(content))

    assert sec_a == sec_b

    # Different data → not equal
    sec_c = _YearValueSection()
    sec_c.read(
        _build_file(
            [
                "HDR\n",
                "1999    9.99\n",
                "\n",
            ]
        )
    )
    assert sec_a != sec_c

    # Different class → not equal
    sec_d = _TwoHeaderSection()
    assert sec_a != sec_d


# ---------------------------------------------------------------------------
# 19. TabularSection import / re-export
# ---------------------------------------------------------------------------


def test_tabular_section_importable_from_module() -> None:
    """TabularSection is importable directly from cfinterface.components.tabular."""
    from cfinterface.components.tabular import TabularSection as TS

    assert TS is TabularSection


def test_tabular_section_reexported_from_components() -> None:
    """TabularSection is re-exported from cfinterface.components."""
    from cfinterface.components import TabularSection as TS

    assert TS is TabularSection


# ---------------------------------------------------------------------------
# 20. Delimited parsing — TabularParser with delimiter
# ---------------------------------------------------------------------------


def _make_semicolon_parser() -> TabularParser:
    cols = [
        ColumnDef("id", IntegerField(6, 0)),
        ColumnDef("value", FloatField(12, 0, decimal_digits=2)),
        ColumnDef("label", LiteralField(20, 0)),
    ]
    return TabularParser(cols, delimiter=";")


def _make_comma_float_parser() -> TabularParser:
    cols = [
        ColumnDef("x", FloatField(12, 0, decimal_digits=4)),
        ColumnDef("y", FloatField(12, 0, decimal_digits=4)),
    ]
    return TabularParser(cols, delimiter=",")


def test_parse_lines_semicolon_delimited() -> None:
    """3 columns with ';' delimiter: values parsed with correct types."""
    parser = _make_semicolon_parser()
    lines = [
        "1;1.25;alpha\n",
        "2;2.50;beta\n",
        "3;3.75;gamma\n",
    ]
    result = parser.parse_lines(lines)
    assert list(result.keys()) == ["id", "value", "label"]
    assert result["id"] == [1, 2, 3]
    assert abs(result["value"][0] - 1.25) < 1e-6
    assert abs(result["value"][1] - 2.50) < 1e-6
    assert abs(result["value"][2] - 3.75) < 1e-6
    assert result["label"] == ["alpha", "beta", "gamma"]


def test_parse_lines_comma_delimited_floats_with_whitespace() -> None:
    """Comma-delimited floats with surrounding whitespace are correctly stripped."""
    parser = _make_comma_float_parser()
    lines = ["1.5, 2.3\n", " 0.1 , 9.8 \n"]
    result = parser.parse_lines(lines)
    assert abs(result["x"][0] - 1.5) < 1e-6
    assert abs(result["y"][0] - 2.3) < 1e-6
    assert abs(result["x"][1] - 0.1) < 1e-6
    assert abs(result["y"][1] - 9.8) < 1e-6


def test_parse_lines_tab_delimited() -> None:
    """Tab delimiter with LiteralField and IntegerField columns."""
    cols = [
        ColumnDef("name", LiteralField(20, 0)),
        ColumnDef("count", IntegerField(8, 0)),
    ]
    parser = TabularParser(cols, delimiter="\t")
    lines = ["alpha\t42\n", "beta\t7\n"]
    result = parser.parse_lines(lines)
    assert result["name"] == ["alpha", "beta"]
    assert result["count"] == [42, 7]


def test_parse_lines_delimited_missing_tokens_filled_with_none() -> None:
    """A delimited line with fewer tokens than columns fills missing ones with None."""
    parser = _make_semicolon_parser()
    # Only 2 tokens instead of 3 — 'label' column is missing
    lines = ["10;5.00\n"]
    result = parser.parse_lines(lines)
    assert result["id"] == [10]
    assert abs(result["value"][0] - 5.0) < 1e-6
    assert result["label"] == [None]


def test_format_rows_semicolon_delimited() -> None:
    """format_rows with ';' delimiter joins fields with semicolons."""
    parser = _make_semicolon_parser()
    data = {
        "id": [1, 2],
        "value": [1.25, 2.50],
        "label": ["alpha", "beta"],
    }
    lines = parser.format_rows(data)
    assert len(lines) == 2
    for line in lines:
        assert ";" in line
        assert line.endswith("\n")
    # Each formatted line must contain the semicolon separator
    assert lines[0].count(";") >= 2
    assert lines[1].count(";") >= 2


def test_round_trip_delimited() -> None:
    """Delimited parse then format then re-parse reproduces equivalent data."""
    parser = _make_semicolon_parser()
    original_lines = [
        "1;1.25;alpha\n",
        "2;2.50;beta\n",
        "3;3.75;gamma\n",
    ]
    parsed = parser.parse_lines(original_lines)
    formatted = parser.format_rows(parsed)
    reparsed = parser.parse_lines(formatted)
    assert reparsed["id"] == parsed["id"]
    for v1, v2 in zip(reparsed["value"], parsed["value"]):
        assert abs(v1 - v2) < 1e-4
    assert reparsed["label"] == parsed["label"]


def test_delimiter_none_gives_same_results_as_positional() -> None:
    """delimiter=None produces the same output as not passing delimiter at all."""
    cols_explicit = [
        ColumnDef("a", IntegerField(4, 0)),
        ColumnDef("b", IntegerField(4, 4)),
    ]
    cols_default = [
        ColumnDef("a", IntegerField(4, 0)),
        ColumnDef("b", IntegerField(4, 4)),
    ]
    parser_none = TabularParser(cols_explicit, delimiter=None)
    parser_default = TabularParser(cols_default)
    lines = ["   1   2", "   3   4", "   5   6"]
    result_none = parser_none.parse_lines(lines)
    result_default = parser_default.parse_lines(lines)
    assert result_none == result_default


def test_parser_delimiter_property_accessible() -> None:
    """parser.delimiter returns the configured delimiter value."""
    parser_semi = TabularParser(
        [ColumnDef("x", IntegerField(4, 0))], delimiter=";"
    )
    parser_comma = TabularParser(
        [ColumnDef("x", IntegerField(4, 0))], delimiter=","
    )
    parser_none = TabularParser([ColumnDef("x", IntegerField(4, 0))])
    assert parser_semi.delimiter == ";"
    assert parser_comma.delimiter == ","
    assert parser_none.delimiter is None


# ---------------------------------------------------------------------------
# 21. TabularSection with DELIMITER class attribute
# ---------------------------------------------------------------------------


class _SemicolonSection(TabularSection):
    """TabularSection subclass for semicolon-delimited data with 1 header line."""

    COLUMNS = [
        ColumnDef("id", IntegerField(6, 0)),
        ColumnDef("value", FloatField(12, 0, decimal_digits=2)),
        ColumnDef("label", LiteralField(20, 0)),
    ]
    HEADER_LINES = 1
    END_PATTERN = ""
    DELIMITER = ";"


def test_tabular_section_delimited_read() -> None:
    """TabularSection subclass with DELIMITER=';' reads semicolon-delimited data."""
    content = [
        "id;value;label\n",
        "1;1.25;alpha\n",
        "2;2.50;beta\n",
        "3;3.75;gamma\n",
        "\n",
    ]
    sec = _SemicolonSection()
    sec.read(_build_file(content))
    assert sec.data is not None
    assert list(sec.data.keys()) == ["id", "value", "label"]
    assert sec.data["id"] == [1, 2, 3]
    assert abs(sec.data["value"][0] - 1.25) < 1e-6
    assert abs(sec.data["value"][2] - 3.75) < 1e-6
    assert sec.data["label"] == ["alpha", "beta", "gamma"]
