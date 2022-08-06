from typing import Any, Union, Optional, TypeVar, Dict, Type
from abc import ABC, abstractmethod
from struct import iter_unpack, pack


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


class BinaryRepository(Repository):

    T = TypeVar("T")

    # Override
    def read(self, source: Union[str, bytes]) -> Optional[T]:
        """
        Reads a field for extracting information.

        :param line: The line to be read
        :type line: str

        :return: The extracted values, in order
        :rtype: List[Any]
        """
        try:
            if isinstance(source, bytes):
                return self._datatype(
                    "".join(
                        [str(b[0]) for b in iter_unpack(self._format, source)]
                    )
                )
            raise TypeError("Incorrect type")
        except Exception:
            return None

    # Override
    def write(
        self,
        value: str,
        destination: Union[str, bytes],
        starting_position: int,
        ending_position: int,
    ) -> bytes:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of to be written
        :type line: str | None
        :param destination: The place to write the field
        :type destination: str
        :param starting_position: The first position occupied in
            the destination
        :type starting_position: int
        :param ending_position: The last position occupied in the
            destination
        :type ending_position: Any
        :return: The line with the new field information
        :rtype: bytes
        """
        if isinstance(destination, bytes):
            if len(destination) < ending_position:
                destination = destination.ljust(ending_position)
            return (
                destination[:starting_position]
                + pack(self._format, self._datatype(value))
                + destination[ending_position:]
            )
        else:
            raise TypeError(
                f"Trying to write binary data to {type(destination)}"
            )


class TextualRepository(Repository):

    T = TypeVar("T")

    # Override
    def read(self, source: Union[str, bytes]) -> Optional[T]:
        """
        Reads a field for extracting information.

        :param line: The line to be read
        :type line: str
        :return: The extracted value, in order
        :rtype: T
        """
        try:
            if isinstance(source, str):
                return self._datatype(source)
            raise TypeError("Incorrect type")
        except Exception:
            return None

    # Override
    def write(
        self,
        value: str,
        destination: Union[str, bytes],
        starting_position: int,
        ending_position: int,
    ) -> str:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of to be written
        :type line: str | None
        :param destination: The place to write the field
        :type destination: str
        :param starting_position: The first position occupied in
            the destination
        :type starting_position: int
        :param ending_position: The last position occupied in the
            destination
        :type ending_position: Any
        :return: The line with the new field information
        :rtype: str
        """
        if isinstance(destination, str):
            if len(destination) < ending_position:
                destination = destination.ljust(ending_position)
            return (
                destination[:starting_position]
                + value
                + destination[ending_position:]
            )
        else:
            raise TypeError(
                f"Trying to write textual data to {type(destination)}"
            )


def factory(kind: str) -> Type[Repository]:
    mappings: Dict[str, Type[Repository]] = {
        "TEXT": TextualRepository,
        "BINARY": BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
