from typing import Union, Dict, Type
import re
from abc import ABC, abstractmethod


class Repository(ABC):
    @staticmethod
    @abstractmethod
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
        raise NotImplementedError

    @staticmethod
    @abstractmethod
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
        raise NotImplementedError


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


class TextualRepository(Repository):
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
        if isinstance(line, str) and isinstance(pattern, str):
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
        if isinstance(line, str) and isinstance(pattern, str):
            return re.search(pattern, line) is not None
        return False


def factory(kind: str) -> Type[Repository]:
    mappings: Dict[str, Type[Repository]] = {
        "TEXT": TextualRepository,
        "BINARY": BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
