from typing import Union, Dict, Type, IO
import re
from abc import ABC, abstractmethod


class Repository(ABC):
    @staticmethod
    @abstractmethod
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
        raise NotImplementedError

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

    @staticmethod
    @abstractmethod
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
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def write(file: IO, data: Union[str, bytes]) -> int:
        """
        Generic function to perform the writing of the register using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The number of written bytes
        :rtype: int
        """
        raise NotImplementedError


class BinaryRepository(Repository):
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
        if isinstance(pattern, bytes) and isinstance(line, bytes):
            return re.search(pattern, line) is not None
        elif isinstance(pattern, str) and isinstance(line, bytes):
            return re.search(pattern, line.decode("utf-8")) is not None
        return False

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
        return file.read(linesize)

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


def factory(kind: str) -> Type[Repository]:
    mappings: Dict[str, Type[Repository]] = {
        "TEXT": TextualRepository,
        "BINARY": BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
