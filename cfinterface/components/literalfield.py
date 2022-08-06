from typing import Optional, Union
import pandas as pd  # type: ignore
from cfinterface.components.field import Field


class LiteralField(Field):
    """
    Class for representing an literal field for being read from and
    written to a file.
    """

    def __init__(
        self,
        size: int = 80,
        starting_position: int = 0,
        value: Optional[str] = None,
        repository: str = "TEXT",
    ) -> None:
        super().__init__(size, starting_position, value, repository, "c", str)

    # Override
    def read(self, line: Union[str, bytes]) -> Optional[str]:
        self._value = self._interface.read(
            line[self._starting_position : self._ending_position]
        )
        return self._value

    # Override
    def write(self, line: Union[str, bytes]) -> Union[str, bytes]:
        if self.value is None or pd.isnull(self.value):
            value = ""
        else:
            value = str(self.value)
        return self._interface.write(
            value.ljust(self._size),
            line,
            self._starting_position,
            self._ending_position,
        )

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, val: str):
        self._value = val
