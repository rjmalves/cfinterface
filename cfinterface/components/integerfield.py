from typing import Optional, Union
import pandas as pd  # type: ignore
from cfinterface.adapters.field.repository import Repository
from cfinterface.adapters.field.textualrepository import TextualRepository

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
        interface: Repository = TextualRepository(),
    ) -> None:
        super().__init__(size, starting_position, value, interface)

    # Override
    def read(self, line: Union[str, bytes]) -> Optional[int]:
        readline = self._interface.read(line)
        linevalue = readline[
            self._starting_position : self._ending_position
        ].strip()
        self._value = int(linevalue) if linevalue.isdigit() else None
        return self._value

    # Override
    def write(self, line: Union[str, bytes]) -> Union[str, bytes]:
        if self.value is None or pd.isnull(self.value):
            value = "".ljust(self._size)
        else:
            value = str(self.value)
        return self._interface.write(
            value, line, self._starting_position, self._ending_position
        )

    @property
    def value(self) -> Optional[int]:
        return self._value

    @value.setter
    def value(self, val: int):
        self._value = val
