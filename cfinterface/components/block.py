from typing import Any, IO
import re

from cfinterface.components.state import ComponentState


class Block:
    """
    Class for a generic block in a textfile, with given markers
    for beginning and end and reading states.
    """

    BEGIN_PATTERN = ""
    END_PATTERN = ""
    MAX_LINES = 10000

    def __init__(
        self,
        state=ComponentState.NOT_FOUND,
        previous=None,
        next=None,
        data=None,
    ) -> None:
        self.__state = state
        self.__previous = previous
        self.__next = next
        self.__data: Any = data

    def __eq__(self, o: object) -> bool:
        raise NotImplementedError()

    @classmethod
    def begins(cls, line: str):
        """
        Checks if the current line marks the beginning of the block.

        :param line: The candidate line for being the beggining of
            the block.
        :type line: str
        """
        return re.search(cls.BEGIN_PATTERN, line) is not None

    @classmethod
    def ends(cls, line: str):
        """
        Checks if the current line marks the end of the block.

        :param line: The candidate line for being the end of the block.
        :type line: str
        """
        return re.search(cls.END_PATTERN, line) is not None

    def read(self, file: IO) -> bool:
        """
        Generic function to perform the reading of the block using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the reading
        :rtype: bool
        """
        raise NotImplementedError()

    def write(self, file: IO) -> bool:
        """
        Generic function to perform the writing of the block using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the writing
        :rtype: bool
        """
        raise NotImplementedError()

    def read_block(self, file: IO):
        """
        Function that reads the block and evaluates the result.

        :param file: The filepointer
        :type file: IO
        """
        if self.read(file):
            self.__state = ComponentState.READ_SUCCESS
        else:
            self.__state = ComponentState.READ_ERROR

    def write_block(self, file: IO):
        """
        Function that writes the block, if it was succesfully read.

        :param file: The filepointer
        :type file: IO
        """
        if self.__state == ComponentState.READ_SUCCESS:
            if self.write(file):
                self.__state = ComponentState.WRITE_SUCCESS
            else:
                self.__state = ComponentState.WRITE_ERROR

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

    @property
    def success(self) -> bool:
        return self.__state in [
            ComponentState.READ_SUCCESS,
            ComponentState.WRITE_SUCCESS,
        ]
