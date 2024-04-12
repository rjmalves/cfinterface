from typing import Optional
import pandas as pd  # type: ignore
import numpy as np  # type: ignore


from cfinterface.components.field import Field


class IntegerField(Field):
    """
    Class for representing an integer field for being read from and
    written to a file.
    """

    __slots__ = ["__type"]

    TYPES = {
        2: np.int16,
        4: np.int32,
        8: np.int64,
    }

    def __init__(
        self,
        size: int = 8,
        starting_position: int = 0,
        value: Optional[int] = None,
    ) -> None:
        super().__init__(size, starting_position, value)
        self.__type = self.__class__.TYPES.get(size, np.int32)

    # Override
    def _binary_read(self, line: bytes) -> int:
        return int(
            np.frombuffer(
                line[self._starting_position : self._ending_position],
                dtype=self.__type,
                count=1,
            )[0]
        )

    # Override
    def _textual_read(self, line: str) -> int:
        return int(line[self._starting_position : self._ending_position])

    # Override
    def _binary_write(self) -> bytes:
        if self.value is None or pd.isnull(self.value):
            return np.array([0], dtype=self.__type).tobytes()
        else:
            return np.array([self._value], dtype=self.__type).tobytes()

    # Override
    def _textual_write(self) -> str:
        if self.value is None or pd.isnull(self.value):
            value = ""
        else:
            value = str(int(self.value))
        return value.rjust(self.size)

    @property
    def value(self) -> Optional[int]:
        return self._value

    @value.setter
    def value(self, val: int):
        self._value = val
