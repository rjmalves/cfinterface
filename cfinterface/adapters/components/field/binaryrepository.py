from typing import Union, TypeVar, Optional
from struct import iter_unpack, pack

from cfinterface.adapters.components.field.repository import Repository


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
