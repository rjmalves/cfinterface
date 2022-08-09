from typing import Optional
import pandas as pd  # type: ignore
import numpy as np  # type: ignore

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
    ) -> None:
        super().__init__(
            size,
            starting_position,
            value,
        )
        self.__decimal_digits = decimal_digits
        self.__format = format
        self.__sep = sep

    # Override
    def _binary_read(self, line: bytes) -> float:
        return float(
            np.frombuffer(
                line[self._starting_position : self._ending_position],
                dtype=np.float32,
                count=1,
            )[0]
        )

    # Override
    def _textual_read(self, line: str) -> float:
        return float(
            line[self._starting_position : self._ending_position].replace(
                self.__sep, "."
            )
        )

    # Override
    def _binary_write(self) -> bytes:
        if self.value is None or pd.isnull(self.value):
            return np.array([0.0], dtype=np.float32).tobytes()
        else:
            return np.array([self._value], dtype=np.float32).tobytes()

    # Override
    def _textual_write(self) -> str:
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
        return value.rjust(self.size)

    @property
    def value(self) -> Optional[float]:
        return self._value

    @value.setter
    def value(self, val: float):
        self._value = val
