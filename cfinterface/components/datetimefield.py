from typing import Optional, Union
from datetime import datetime
import pandas as pd  # type: ignore
from cfinterface.adapters.field.repository import Repository
from cfinterface.adapters.field.textualrepository import TextualRepository

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
        starting_position: int = 0,
        format: str = "%Y/%m/%d",
        value: Optional[datetime] = None,
        interface: Repository = TextualRepository(),
    ) -> None:
        super().__init__(size, starting_position, value, interface)
        self.__format = format

    # Override
    def read(self, line: Union[str, bytes]) -> Optional[datetime]:
        readline = self._interface.read(line)
        linevalue = readline[
            self._starting_position : self._ending_position
        ].strip()
        try:
            self._value = datetime.strptime(linevalue, self.__format)
        except ValueError:
            self._value = None
        return self._value

    # Override
    def write(self, line: Union[str, bytes]) -> str:
        value = "".ljust(self._size)
        if self.value is not None and not pd.isnull(self.value):
            value = self.value.strftime(self.__format)
        return self._interface.write(
            value, line, self._starting_position, self._ending_position
        )

    @property
    def value(self) -> Optional[datetime]:
        return self._value

    @value.setter
    def value(self, val: datetime):
        self._value = val
