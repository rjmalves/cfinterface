from typing import IO, Union
import re

from cfinterface.adapters.components.register.repository import Repository


class TextualRepository(Repository):
    @staticmethod
    def matches(pattern: Union[str, bytes], line: Union[str, bytes]) -> bool:
        """
        Checks if the current line matches the identifier of the register.

        :param pattern: The pattern for matching the register
        :type pattern: str | bytes
        :param line: The candidate line for containing
            the register information
        :type line: str | bytes
        :return: The register in the current line
        :rtype: bool
        """
        if isinstance(pattern, str) and isinstance(line, str):
            return re.search(pattern, line) is not None
        return False

    @staticmethod
    def read(file: IO, linesize: int) -> Union[str, bytes]:
        """
        Generic function to perform the reading of the register using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :param linesize: The size of the line to be read
        :type linesize: int
        :return: The read data
        :rtype: str | bytes
        """
        return file.readline()

    @staticmethod
    def write(file: IO, data: Union[str, bytes]) -> int:
        """
        Generic function to perform the writing of the register using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The number of written bytes
        :rtype: int
        """
        return file.write(data)
