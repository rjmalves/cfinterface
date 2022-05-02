from typing import Any, IO
import re

from cfinterface.components.state import ComponentState
from cfinterface.components.line import Line


class Register:
    """
    Class for a generic register in a textfile, with a given identifier
    which is located at the beginning of the line.
    """

    IDENTIFIER = ""
    IDENTIFIER_DIGITS = 0
    LINE = Line([])

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
        if not isinstance(o, self.__class__):
            return False
        else:
            return o.data == self.data

    @classmethod
    def matches(cls, line: str):
        """
        Checks if the current line matches the identifier of the register.

        :param line: The candidate line for containing
            the register information
        :type line: str
        """
        return (
            re.search(cls.IDENTIFIER, line[: cls.IDENTIFIER_DIGITS])
            is not None
        )

    def read(self, file: IO) -> bool:
        """
        Generic function to perform the reading of the register using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the reading
        :rtype: bool
        """
        self.data = self.__class__.LINE.read(file.readline())
        return True

    def write(self, file: IO) -> bool:
        """
        Generic function to perform the writing of the register using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the writing
        :rtype: bool
        """
        line = self.__class__.LINE.write(self.data)
        line = (
            self.__class__.IDENTIFIER.ljust(self.__class__.IDENTIFIER_DIGITS)
            + line[self.__class__.IDENTIFIER_DIGITS :]
        )
        file.write(line)
        return True

    def read_register(self, file: IO):
        """
        Function that reads the register and evaluates the result.

        :param file: The filepointer
        :type file: IO
        """
        if self.read(file):
            self.__state = ComponentState.READ_SUCCESS
        else:
            self.__state = ComponentState.READ_ERROR

    def write_register(self, file: IO):
        """
        Function that writes the register, if it was succesfully read.

        :param file: The filepointer
        :type file: IO
        """
        if self.__state == ComponentState.READ_SUCCESS:
            if self.write(file):
                self.__state = ComponentState.WRITE_SUCCESS
            else:
                self.__state = ComponentState.WRITE_ERROR

    @property
    def previous(self) -> "Register":
        return self.__previous

    @previous.setter
    def previous(self, b: "Register"):
        self.__previous = b

    @property
    def next(self) -> "Register":
        return self.__next

    @next.setter
    def next(self, b: "Register"):
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
