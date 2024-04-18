from datetime import datetime
import pandas as pd  # type: ignore
from typing import Optional, Union, List

from cfinterface.components.field import Field


class DatetimeField(Field):
    """
    Class for representing an datetime field for being read from and
    written to a file. The format to read and write the value is given
    by an optional argument.
    """

    __slots__ = ["__format"]

    def __init__(
        self,
        size: int = 16,
        starting_position: int = 0,
        format: Union[str, List[str]] = "%Y/%m/%d",
        value: Optional[datetime] = None,
    ) -> None:
        super().__init__(size, starting_position, value)
        self.__format = format

    # Override
    def _binary_read(self, line: bytes) -> datetime:
        formats = (
            [self.__format]
            if isinstance(self.__format, str)
            else self.__format
        )
        for fmt in formats:
            try:
                return datetime.strptime(
                    line[self._starting_position : self._ending_position]
                    .decode("utf-8")
                    .strip(),
                    fmt,
                )
            except ValueError:
                pass
        raise ValueError("Could not read datetime")

    # Override
    def _textual_read(self, line: str) -> datetime:
        formats = (
            [self.__format]
            if isinstance(self.__format, str)
            else self.__format
        )
        for fmt in formats:
            try:
                return datetime.strptime(
                    line[
                        self._starting_position : self._ending_position
                    ].strip(),
                    fmt,
                )
            except ValueError:
                pass
        raise ValueError("Could not read datetime")

    # Override
    def _binary_write(self) -> bytes:
        if self.value is None or pd.isnull(self.value):
            return b"".ljust(self.size)
        else:
            format = (
                self.__format
                if isinstance(self.__format, str)
                else self.__format[0]
            )
            return self.value.strftime(format).ljust(self.size).encode("utf-8")

    # Override
    def _textual_write(self) -> str:
        if self.value is None or pd.isnull(self.value):
            value = ""
        else:
            format = (
                self.__format
                if isinstance(self.__format, str)
                else self.__format[0]
            )
            value = self.value.strftime(format)
        return value.ljust(self._size)

    @property
    def value(self) -> Optional[datetime]:
        return self._value

    @value.setter
    def value(self, val: datetime):
        self._value = val
