from math import floor, log10

import numpy as np  # type: ignore[import-untyped]

from cfinterface._utils import _is_null
from cfinterface.components.field import Field


class FloatField(Field):
    """
    Class for representing an float field for being read from and
    written to a file. The format to read and write the value is given
    by 'F' for fixed point notation and 'E' or 'D' for scientific notation.
    """

    __slots__ = ["__decimal_digits", "__format", "__sep", "__type"]

    TYPES = {
        2: np.float16,
        4: np.float32,
        8: np.float64,
    }

    def __init__(
        self,
        size: int = 8,
        starting_position: int = 0,
        decimal_digits: int = 4,
        format: str = "F",
        sep: str = ".",
        value: float | None = None,
    ) -> None:
        super().__init__(
            size,
            starting_position,
            value,
        )
        self.__decimal_digits = decimal_digits
        self.__format = format
        self.__sep = sep
        self.__type = self.__class__.TYPES.get(size, np.float32)

    def _binary_read(self, line: bytes) -> float:
        return float(
            np.frombuffer(
                line[self._starting_position : self._ending_position],
                dtype=self.__type,
                count=1,
            )[0]
        )

    def _textual_read(self, line: str) -> float:
        return float(
            line[self._starting_position : self._ending_position]
            .replace(self.__sep, ".")
            .replace("D", "E")
            .replace("d", "e")
        )

    def _binary_write(self) -> bytes:
        if self.value is None or _is_null(self.value):
            return np.array([0.0], dtype=self.__type).tobytes()
        else:
            return np.array([self._value], dtype=self.__type).tobytes()

    def _textual_write(self) -> str:
        value = ""
        if self.value is not None and not _is_null(self.value):
            if self.__format.lower() == "e" and self.value != 0:
                value = "{:.{d}{format}}".format(
                    round(
                        self.value,
                        self.__decimal_digits
                        - int(floor(log10(abs(self.value)))),
                    ),
                    d=self.__decimal_digits,
                    format=self.__format,
                )
                value = value[: self.size]
            elif self.__format.lower() == "d" and self.value != 0:
                value = "{:.{d}{format}}".format(
                    round(
                        self.value,
                        self.__decimal_digits
                        - int(floor(log10(abs(self.value)))),
                    ),
                    d=self.__decimal_digits,
                    format="E",
                ).replace("E", "D")
                value = value[: self.size]
            else:
                formatting_format = (
                    "E" if self.__format.lower() == "d" else self.__format
                )
                value = "{:.{d}{format}}".format(
                    round(self.value, self.__decimal_digits),
                    d=self.__decimal_digits,
                    format=formatting_format,
                ).replace("E", self.__format)
                if len(value) > self._size:
                    excess = len(value) - self._size
                    new_d = self.__decimal_digits - excess
                    if new_d < 0:
                        new_d = 0
                    value = "{:.{d}{format}}".format(
                        round(self.value, new_d),
                        d=new_d,
                        format=formatting_format,
                    ).replace("E", self.__format)
                    if len(value) > self._size:
                        new_d = max(0, new_d - 1)
                        value = "{:.{d}{format}}".format(
                            round(self.value, new_d),
                            d=new_d,
                            format=formatting_format,
                        ).replace("E", self.__format)
        return value.rjust(self.size)

    @property
    def value(self) -> float | None:
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        self._value = val
