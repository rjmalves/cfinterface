from typing import Optional, Union
import pandas as pd  # type: ignore


from cfinterface.components.field import Field


class IntegerField(Field):
    """
    Class for representing an integer field for being read from and
    written to a file.
    """

    def __init__(
        self,
        size: int = 16,
        starting_position: int = 0,
        value: Optional[int] = None,
        repository: str = "TEXT",
    ) -> None:
        super().__init__(size, starting_position, value, repository, "i", int)

    # Override
    def read(self, line: Union[str, bytes]) -> Optional[int]:
        self._value = self._interface.read(
            line[self._starting_position : self._ending_position]
        )
        return self._value

    # Override
    def write(self, line: Union[str, bytes]) -> Union[str, bytes]:
        if self.value is None or pd.isnull(self.value):
            value = ""
        else:
            value = str(int(self.value))
        return self._interface.write(
            value.rjust(self._size),
            line,
            self._starting_position,
            self._ending_position,
        )

    @property
    def value(self) -> Optional[int]:
        return self._value

    @value.setter
    def value(self, val: int):
        self._value = val
