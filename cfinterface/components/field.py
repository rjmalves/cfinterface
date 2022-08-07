from typing import Any, Optional, Union

from cfinterface.adapters.components.field.repository import factory


class Field:
    """
    Class for representing an field for being read from and written
    in a file.
    """

    def __init__(
        self,
        size: int,
        starting_position: int,
        value: Optional[Any] = None,
        storage: str = "",
        format: str = "c",
        datatype: type = str,
    ) -> None:
        self._size = size
        self._starting_position = starting_position
        self._ending_position = size + starting_position
        self._value = value
        self._storage = storage
        self._dataformat = format
        self._datatype = datatype
        self._repository = factory(self._storage)(
            self._dataformat, self._datatype
        )

    def read(self, line: Union[str, bytes]) -> Any:
        """
        Generic method for reading a field from a given line of a file.

        :param line: The line read from the file
        :type line: Union[str, bytes]
        :return: The value read from the field
        :rtype: Any
        """
        raise NotImplementedError

    def write(self, line: Union[str, bytes]) -> Any:
        """
        Generic method for writing a field to a given line of a file.

        :param line: The line read from the file
        :type line: Union[str, bytes]
        :return: The value read from the field
        :rtype: Any
        """
        raise NotImplementedError

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, val: int):
        self._size = val

    @property
    def storage(self) -> str:
        return self._storage

    @storage.setter
    def storage(self, s: str):
        self._storage = s
        self._repository = factory(s)(self._dataformat, self._datatype)

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
