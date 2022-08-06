from typing import Any, Union
from abc import ABC, abstractmethod


class Repository(ABC):
    def __init__(self, format: str, datatype: type) -> None:
        self._format = format
        self._datatype: type = datatype

    @abstractmethod
    def read(self, source: Union[str, bytes]) -> Any:
        """
        Reads a field for extracting information.

        :param source: The source to be read
        :type source: Union[str, bytes]
        :return: The extracted value
        :rtype: Any
        """
        raise NotImplementedError

    @abstractmethod
    def write(
        self,
        value: Any,
        destination: Any,
        starting_position: int,
        ending_position: int,
    ) -> Any:
        """
        Writes a field with the existing information.

        :param value: The value of the field
        :type value: Any
        :param destination: The place to write the field
        :type destination: Any
        :param starting_position: The first position occupied in
            the destination
        :type starting_position: int
        :param ending_position: The last position occupied in the
            destination
        :type ending_position: Any
        :return: The new field information
        :rtype: Any
        """
        raise NotImplementedError
