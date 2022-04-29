from typing import Optional

from cfinterface.components.field import Field


class IntegerField(Field):
    """
    Class for representing an integer field for being read from and
    written to a file.
    """

    def __init__(
        self, size: int, starting_column: int, value: Optional[int] = None
    ) -> None:
        super().__init__(size, starting_column, value)

    # Override
    def read(self, line: str) -> Optional[int]:
        linevalue = line[self._starting_column : self._ending_column].strip()
        self._value = int(linevalue) if linevalue.isdigit() else None
        return self._value

    # Override
    def write(self, line: str) -> str:
        if self.value is None:
            value = ""
        else:
            value = str(self.value)
        if len(line) < self._ending_column:
            line = line.ljust(self._ending_column)
        return (
            line[: self._starting_column]
            + value.rjust(self._size)
            + line[self._ending_column :]
        )

    @property
    def value(self) -> Optional[int]:
        return self._value

    @value.setter
    def value(self, val: int):
        self._value = val
