from typing import Optional
from datetime import datetime

from cfinterface.components.field import Field


class DatetimeField(Field):
    """
    Class for representing an datetime field for being read from and
    written to a file. The format to read and write the value is given
    by an optional argument.
    """

    def __init__(
        self,
        size: int = 16,
        starting_column: int = 0,
        format: str = "%Y/%m/%d",
        value: Optional[datetime] = None,
    ) -> None:
        super().__init__(size, starting_column, value)
        self.__format = format

    # Override
    def read(self, line: str) -> Optional[datetime]:
        linevalue = line[self._starting_column : self._ending_column].strip()
        try:
            self._value = datetime.strptime(linevalue, self.__format)
        except ValueError:
            self._value = None
        return self._value

    # Override
    def write(self, line: str) -> str:
        if len(line) < self._ending_column:
            line = line.ljust(self._ending_column)
        value = ""
        if self.value is not None:
            value = self.value.strftime(self.__format)
        return (
            line[: self._starting_column]
            + value.rjust(self._size)
            + line[self._ending_column :]
        )

    @property
    def value(self) -> Optional[datetime]:
        return self._value

    @value.setter
    def value(self, val: datetime):
        self._value = val
