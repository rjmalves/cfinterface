from typing import Optional

from cfinterface.components.field import Field


class LiteralField(Field):
    """
    Class for representing an literal field for being read from and
    written to a file.
    """

    def __init__(
        self, size: int, starting_column: int, value: Optional[str] = None
    ) -> None:
        super().__init__(size, starting_column, value)

    # Override
    def read(self, line: str) -> str:
        self._value = line[self._starting_column : self._ending_column].strip()
        return self._value

    # Override
    def write(self, line: str) -> str:
        if self.value is None:
            value = ""
        else:
            value = self.value
        if len(line) < self._ending_column:
            line = line.ljust(self._ending_column)
        return (
            line[: self._starting_column]
            + value.ljust(self._size)
            + line[self._ending_column :]
        )

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, val: str):
        self._value = val
