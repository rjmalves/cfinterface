
import numpy as np  # type: ignore[import-untyped]

from cfinterface._utils import _is_null
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
        value: int | None = None,
    ) -> None:
        super().__init__(size, starting_position, value)
        self.__type = self.__class__.TYPES.get(size, np.int32)

    def _binary_read(self, line: bytes) -> int:
        return int(
            np.frombuffer(
                line[self._starting_position : self._ending_position],
                dtype=self.__type,
                count=1,
            )[0]
        )

    def _textual_read(self, line: str) -> int:
        return int(line[self._starting_position : self._ending_position])

    def _binary_write(self) -> bytes:
        if self.value is None or _is_null(self.value):
            return np.array([0], dtype=self.__type).tobytes()
        else:
            return np.array([self._value], dtype=self.__type).tobytes()

    def _textual_write(self) -> str:
        if self.value is None or _is_null(self.value):
            value = ""
        else:
            value = str(int(self.value))
        return value.rjust(self.size)

    @property
    def value(self) -> int | None:
        return self._value

    @value.setter
    def value(self, val: int) -> None:
        self._value = val
