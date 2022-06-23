from typing import Any, Optional


class Field:
    """
    Class for representing an field for being read from and written
    in a file.
    """

    def __init__(
        self, size: int, starting_column: int, value: Optional[Any] = None
    ) -> None:
        self._size = size
        self._starting_column = starting_column
        self._ending_column = size + starting_column
        self._value = value

    def read(self, line: str) -> Any:
        """
        Generic method for reading a field from a given line of a file.

        :param line: The line read from the file
        :type line: str
        :return: The value read from the field
        :rtype: Any
        """
        raise NotImplementedError()

    def write(self, line: str) -> str:
        """
        Generic method for writing a field to a given line of a file.

        :param line: The line read from the file
        :type line: str
        :return: The value read from the field
        :rtype: Any
        """
        raise NotImplementedError()

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, val: int):
        self._size = val

    @property
    def starting_column(self) -> int:
        return self._starting_column

    @starting_column.setter
    def starting_column(self, val: int):
        self._starting_column = val

    @property
    def ending_column(self) -> int:
        return self._ending_column

    @ending_column.setter
    def ending_column(self, val: int):
        self._ending_column = val

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, val: Any):
        self._value = val
