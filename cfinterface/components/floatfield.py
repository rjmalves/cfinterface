from typing import Optional

from cfinterface.components.field import Field


class FloatField(Field):
    """
    Class for representing an float field for being read from and
    written to a file. The format to read and write the value is given
    by 'F' for fixed point notation and 'E' for scientific notation.
    """

    def __init__(
        self,
        size: int,
        starting_column: int,
        decimal_digits: int,
        format: str = "F",
        sep: str = ".",
        value: Optional[float] = None,
    ) -> None:
        super().__init__(size, starting_column, value)
        self.__decimal_digits = decimal_digits
        self.__format = format
        self.__sep = sep

    # Override
    def read(self, line: str) -> Optional[float]:
        linevalue = (
            line[self._starting_column : self._ending_column]
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
    def write(self, line: str) -> str:
        if len(line) < self._ending_column:
            line = line.ljust(self._ending_column)
        value = ""
        if self.value is not None:
            for d in range(self.__decimal_digits, -1, -1):
                value = "{:.{d}{format}}".format(
                    round(self.value, d),
                    d=d,
                    format=self.__format,
                )
                if len(value) <= self._size:
                    break

        return (
            line[: self._starting_column]
            + value.rjust(self._size)
            + line[self._ending_column :]
        )

    @property
    def value(self) -> Optional[float]:
        return self._value

    @value.setter
    def value(self, val: float):
        self._value = val
