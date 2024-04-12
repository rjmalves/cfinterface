from typing import Any, IO, Union

from cfinterface.adapters.components.repository import factory


class Block:
    """
    Class for a generic block in a textfile, with given markers
    for beginning and end and reading states.
    """

    __slots__ = ["__previous", "__next", "__data"]

    BEGIN_PATTERN: Union[str, bytes] = ""
    END_PATTERN: Union[str, bytes] = ""
    MAX_LINES = 10000

    def __init__(
        self,
        previous=None,
        next=None,
        data=None,
    ) -> None:
        self.__previous = previous
        self.__next = next
        self.__data: Any = data

    def __eq__(self, o: object) -> bool:
        raise NotImplementedError

    @classmethod
    def begins(cls, line: Union[str, bytes], storage: str = ""):
        """
        Checks if the current line marks the beginning of the block.

        :param line: The candidate line for being the beggining of
            the block.
        :type line: str | bytes
        """
        return factory(storage).begins(cls.BEGIN_PATTERN, line)

    @classmethod
    def ends(cls, line: Union[str, bytes], storage: str = ""):
        """
        Checks if the current line marks the end of the block.

        :param line: The candidate line for being the end of the block.
        :type line: str | bytes
        """
        return factory(storage).ends(cls.END_PATTERN, line)

    def read(self, file: IO, *args, **kwargs) -> bool:
        """
        Generic function to perform the reading of the block using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the reading
        :rtype: bool
        """
        raise NotImplementedError

    def write(self, file: IO, *args, **kwargs) -> bool:
        """
        Generic function to perform the writing of the block using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the writing
        :rtype: bool
        """
        raise NotImplementedError

    def read_block(self, file: IO, *args, **kwargs):
        """
        Function that reads the block and evaluates the result.

        :param file: The filepointer
        :type file: IO
        """
        self.read(file, *args, **kwargs)

    def write_block(self, file: IO, *args, **kwargs):
        """
        Function that writes the block, if it was succesfully read.

        :param file: The filepointer
        :type file: IO
        """
        self.write(file, *args, **kwargs)

    @property
    def previous(self) -> "Block":
        return self.__previous

    @previous.setter
    def previous(self, b: "Block"):
        self.__previous = b

    @property
    def next(self) -> "Block":
        return self.__next

    @next.setter
    def next(self, b: "Block"):
        self.__next = b

    @property
    def data(self) -> Any:
        return self.__data

    @data.setter
    def data(self, d: Any):
        self.__data = d

    @property
    def is_first(self) -> bool:
        return self.__previous is None

    @property
    def is_last(self) -> bool:
        return self.__next is None

    @property
    def empty(self) -> bool:
        return self.__data is None
