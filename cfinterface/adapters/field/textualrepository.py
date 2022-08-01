from typing import Union

from cfinterface.adapters.field.repository import Repository


class TextualRepository(Repository):

    # Override
    def read(self, source: Union[str, bytes]) -> str:
        """
        Reads a field for extracting information.

        :param line: The line to be read
        :type line: str
        :return: The extracted values, in order
        :rtype: List[Any]
        """
        if isinstance(source, str):
            return source
        else:
            raise TypeError(f"Trying to read textual data from {type(source)}")

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
