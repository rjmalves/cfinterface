from typing import Any
from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def read(self, source: Any) -> str:
        """
        Reads a field for extracting information.

        :param source: The source to be read
        :type source: Any
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
