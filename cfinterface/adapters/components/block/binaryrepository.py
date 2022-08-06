from typing import Union
import re

from cfinterface.adapters.components.block.repository import Repository


class BinaryRepository(Repository):
    @staticmethod
    def begins(pattern: Union[str, bytes], line: Union[str, bytes]) -> bool:
        """
         Checks if the current line marks the beginning of the block.

        :param pattern: The pattern for matching the beginning
        :type pattern: str | bytes
        :param line: The candidate line for being the beginning of
            the block.
        :type line: str | bytes
        :return: The beginning of the block in the current line
        :rtype: bool
        """
        if isinstance(line, bytes) and isinstance(pattern, bytes):
            return re.search(pattern, line) is not None
        return False

    @staticmethod
    def ends(pattern: Union[str, bytes], line: Union[str, bytes]) -> bool:
        """
        Checks if the current line marks the end of the block.

        :param pattern: The pattern for matching the ending
        :type pattern: str | bytes
        :param line: The candidate line for being the ending of
            the block.
        :type line: str | bytes
        :return: The ending of the block in the current line
        :rtype: bool
        """
        if isinstance(line, bytes) and isinstance(pattern, bytes):
            return re.search(pattern, line) is not None
        return False
