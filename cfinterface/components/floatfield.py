from typing import Optional, Union
import pandas as pd  # type: ignore
from cfinterface.adapters.field.repository import Repository
from cfinterface.adapters.field.textualrepository import TextualRepository

from cfinterface.components.field import Field


class FloatField(Field):
    """
    Class for representing an float field for being read from and
    written to a file. The format to read and write the value is given
    by 'F' for fixed point notation and 'E' for scientific notation.
    """

    def __init__(
        self,
        size: int = 16,
        starting_position: int = 0,
        decimal_digits: int = 4,
        format: str = "F",
        sep: str = ".",
        value: Optional[float] = None,
        interface: Repository = TextualRepository(),
    ) -> None:
        super().__init__(size, starting_position, value, interface)
        self.__decimal_digits = decimal_digits
        self.__format = format
        self.__sep = sep

    # Override
    def read(self, line: Union[str, bytes]) -> Optional[float]:
        readline = self._interface.read(line)
        linevalue = (
            readline[self._starting_position : self._ending_position]
            .strip()
            .replace(self.__sep, ".")
        )
        self._value = (
            float(linevalue)
            if linevalue.replace(".", "")
            .replace(self.__format, "")
            .replace("+", "")
            .replace("-", "")
            .isdigit()
            else None
        )
        return self._value

    # Override
    def write(self, line: Union[str, bytes]) -> Union[str, bytes]:
        value = ""
        if self.value is not None and not pd.isnull(self.value):
            for d in range(self.__decimal_digits, -1, -1):
                value = "{:.{d}{format}}".format(
                    round(self.value, d),
                    d=d,
                    format=self.__format,
                )
                if len(value) <= self._size:
                    break

        return self._interface.write(
            value.rjust(self._size),
            line,
            self._starting_position,
            self._ending_position,
        )

    @property
    def value(self) -> Optional[float]:
        return self._value

    @value.setter
    def value(self, val: float):
        self._value = val
