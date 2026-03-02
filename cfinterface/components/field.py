from abc import abstractmethod
from typing import Any, TypeVar, overload

_T = TypeVar("_T", str, bytes)


class Field:
    """
    Class for representing an field for being read from and written
    in a file.
    """

    __slots__ = ["_size", "_starting_position", "_ending_position", "_value"]

    def __init__(
        self,
        size: int,
        starting_position: int,
        value: Any | None = None,
    ) -> None:
        self._size = size
        self._starting_position = starting_position
        self._ending_position = size + starting_position
        self._value = value

    @abstractmethod
    def _binary_read(self, line: bytes) -> Any:
        raise NotImplementedError

    @abstractmethod
    def _textual_read(self, line: str) -> Any:
        raise NotImplementedError

    @overload
    def read(self, line: str) -> Any: ...

    @overload
    def read(self, line: bytes) -> Any: ...

    def read(self, line: _T) -> Any:
        try:
            if isinstance(line, bytes):
                self._value = self._binary_read(line)
            else:
                self._value = self._textual_read(line)
        except ValueError:
            self._value = None
        return self._value

    @abstractmethod
    def _binary_write(self) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def _textual_write(self) -> str:
        raise NotImplementedError

    @overload
    def write(self, line: str) -> str: ...

    @overload
    def write(self, line: bytes) -> bytes: ...

    def write(self, line: _T) -> _T:
        if isinstance(line, bytes):
            value = self._binary_write()
        else:
            value = self._textual_write()
        if len(line) < self.ending_position:
            line = line.ljust(self.ending_position)
        return (
            line[: self.starting_position]
            + value
            + line[self.ending_position :]
        )

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, val: int) -> None:
        self._size = val

    @property
    def starting_position(self) -> int:
        return self._starting_position

    @starting_position.setter
    def starting_position(self, val: int) -> None:
        self._starting_position = val

    @property
    def ending_position(self) -> int:
        return self._ending_position

    @ending_position.setter
    def ending_position(self, val: int) -> None:
        self._ending_position = val

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, val: Any) -> None:
        self._value = val
