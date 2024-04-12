from abc import abstractmethod
from typing import Any, Optional, Union, TypeVar


class Field:
    """
    Class for representing an field for being read from and written
    in a file.
    """

    __slots__ = ["_size", "_starting_position", "_ending_position", "_value"]

    T = TypeVar("T", str, bytes)

    def __init__(
        self,
        size: int,
        starting_position: int,
        value: Optional[Any] = None,
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

    def read(self, line: T) -> Any:
        """
        Generic method for reading a field from a given line of a file.

        :param line: The line read from the file
        :type line: Union[str, bytes]
        :return: The value read from the field
        :rtype: Any
        """
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

    def write(self, line: T) -> T:
        """
        Generic method for writing a field to a given line of a file.

        :param line: The line read from the file
        :type line: Union[str, bytes]
        :return: The value written to the field
        :rtype: Union[str, bytes]
        """
        value: Union[str, bytes] = ""
        if isinstance(line, bytes):
            value = self._binary_write()
        else:
            value = self._textual_write()

        if len(line) < self.ending_position:
            line = line.ljust(self.ending_position)

        if isinstance(value, str) and isinstance(line, str):
            return (
                line[: self.starting_position]
                + value
                + line[self.ending_position :]
            )
        elif isinstance(value, bytes) and isinstance(line, bytes):
            return (
                line[: self.starting_position]
                + value
                + line[self.ending_position :]
            )
        else:
            return line

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, val: int):
        self._size = val

    @property
    def starting_position(self) -> int:
        return self._starting_position

    @starting_position.setter
    def starting_position(self, val: int):
        self._starting_position = val

    @property
    def ending_position(self) -> int:
        return self._ending_position

    @ending_position.setter
    def ending_position(self, val: int):
        self._ending_position = val

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, val: Any):
        self._value = val
