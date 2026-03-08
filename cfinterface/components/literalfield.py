from cfinterface._utils import _is_null
from cfinterface.components.field import Field


class LiteralField(Field):
    """
    Class for representing an literal field for being read from and
    written to a file.
    """

    __slots__ = []

    def __init__(
        self,
        size: int = 80,
        starting_position: int = 0,
        value: str | None = None,
    ) -> None:
        super().__init__(size, starting_position, value)

    def _binary_read(self, line: bytes) -> str:
        return (
            line[self._starting_position : self._ending_position]
            .decode("utf-8")
            .strip()
        )

    def _textual_read(self, line: str) -> str:
        return line[self._starting_position : self._ending_position].strip()

    def _binary_write(self) -> bytes:
        if self.value is None or _is_null(self.value):
            return b"".ljust(self.size)
        else:
            return self.value.ljust(self.size).encode("utf-8")

    def _textual_write(self) -> str:
        if self.value is None or _is_null(self.value):
            value = ""
        else:
            value = str(self.value)
        return value.ljust(self._size)

    @property
    def value(self) -> str | None:
        return self._value

    @value.setter
    def value(self, val: str) -> None:
        self._value = val
