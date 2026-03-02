import re
from typing import IO, Any, NamedTuple, cast

from cfinterface.components.field import Field
from cfinterface.components.line import Line
from cfinterface.components.section import Section
from cfinterface.storage import StorageType


class ColumnDef(NamedTuple):
    """
    Named tuple defining a single column in a tabular layout.

    Each ColumnDef must use its own Field instance; Line.read() mutates
    field values in place, so sharing Field instances across columns
    produces incorrect results.
    """

    name: str
    field: Field


class TabularParser:
    """
    Transforms lists of text lines into a dict-of-lists keyed by column name,
    and provides the inverse format_rows() operation.

    Supports both fixed-width positional parsing (``delimiter=None``, the
    default) and delimiter-separated parsing.  For delimited lines each token
    is stripped of whitespace before being passed to the field reader;
    ``field.starting_position`` is ignored and only ``field.size`` (maximum
    token width) applies.

    Note: splitting uses ``str.split(delimiter)`` and does not support
    quoted fields.
    """

    __slots__ = ["_columns", "_delimiter", "_line"]

    def __init__(
        self,
        columns: list[ColumnDef],
        storage: str | StorageType = "",
        delimiter: str | bytes | None = None,
    ) -> None:
        self._columns = columns
        self._delimiter = delimiter
        self._line = Line(
            [col.field for col in columns],
            delimiter=delimiter,
            storage=storage,
        )

    @property
    def delimiter(self) -> str | bytes | None:
        return self._delimiter

    def parse_lines(self, lines: list[str]) -> dict[str, list[Any]]:
        """
        Parse raw text lines into a dict-of-lists keyed by column name.

        Lines that raise an exception during reading are filled with
        ``None`` for every column so that row counts always match input
        length.
        """
        names = [col.name for col in self._columns]
        result: dict[str, list[Any]] = {name: [] for name in names}
        for line in lines:
            try:
                values: list[Any] = self._line.read(line)
            except Exception:
                values = [None] * len(self._columns)
            for name, val in zip(names, values, strict=False):
                result[name].append(val)
        return result

    def format_rows(self, data: dict[str, list[Any]]) -> list[str]:
        """
        Format a dict-of-lists into text lines — the inverse of parse_lines().

        Returns one line per row; each line ends with ``\\n`` because
        Line.write() always appends one.
        """
        names = [col.name for col in self._columns]
        n_rows = len(next(iter(data.values()))) if data else 0
        result: list[str] = []
        for i in range(n_rows):
            values = [data[name][i] for name in names]
            result.append(cast(str, self._line.write(values)))
        return result

    @staticmethod
    def to_dataframe(data: dict[str, list[Any]]) -> "pd.DataFrame":  # type: ignore[name-defined]  # noqa: F821
        """
        Convert a dict-of-lists to a pandas DataFrame.

        Raises ``ImportError`` if pandas is not installed.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this operation. "
                "Install it with: pip install cfinterface[pandas]"
            ) from None
        return pd.DataFrame(data)


class TabularSection(Section):
    """
    Base class for fixed-width (or delimiter-separated) tabular sections.

    Subclasses override the class attributes to declare the format and
    inherit fully functional ``read()`` / ``write()`` methods.

    Class Attributes
    ----------------
    COLUMNS : List[ColumnDef]
        Ordered column specifications.
    HEADER_LINES : int
        Lines before the data block; captured and replayed verbatim.
    END_PATTERN : str
        Regex that terminates reading (file pointer rewound to that line).
        Empty string disables the check.
    DELIMITER : Optional[Union[str, bytes]]
        Field separator; ``None`` selects fixed-width positional parsing.
    """

    __slots__ = ["_parser", "_headers"]

    COLUMNS: list[ColumnDef] = []
    HEADER_LINES: int = 0
    END_PATTERN: str = ""
    DELIMITER: str | bytes | None = None

    def __init__(
        self,
        previous: Any | None = None,
        next: Any | None = None,
        data: Any | None = None,
    ) -> None:
        super().__init__(previous, next, data)
        self._parser = TabularParser(
            self.__class__.COLUMNS,
            storage=self.__class__.STORAGE,
            delimiter=self.__class__.DELIMITER,
        )
        self._headers: list[str] = []

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        self._headers = []
        for _ in range(self.__class__.HEADER_LINES):
            self._headers.append(file.readline())

        lines: list[str] = []
        end_pattern = self.__class__.END_PATTERN
        while True:
            pos = file.tell()
            line = file.readline()
            if line == "" or len(line) <= 1:
                break
            if end_pattern and re.search(end_pattern, line):
                file.seek(pos)
                break
            lines.append(line)

        self.data = self._parser.parse_lines(lines)
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        for header in self._headers:
            file.write(header)
        if self.data is not None:
            for line in self._parser.format_rows(self.data):
                file.write(line)
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return self.data == o.data  # type: ignore[no-any-return]
