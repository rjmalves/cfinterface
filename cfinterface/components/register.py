from typing import Any, IO
import re
from cfinterface.components.field import Field

from cfinterface.components.literalfield import LiteralField
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
        previous=None,
        next=None,
        data=None,
    ) -> None:
        identifier_field: Field = LiteralField(
            self.__class__.IDENTIFIER_DIGITS, 0
        )
        self.__line = Line(
            [identifier_field] + self.__class__.LINE.fields,
            delimiter=self.__class__.LINE.delimiter,
        )
        self.__previous = previous
        self.__next = next
        if data is None:
            self.__data = [None] * len(self.__class__.LINE.fields)
        else:
            self.__data = data

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
        self.data = self.__line.read(file.readline())[1:]
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
        line = self.__line.write([self.__class__.IDENTIFIER] + self.data)
        file.write(line)
        return True

    def read_register(self, file: IO):
        """
        Function that reads the register and evaluates the result.

        :param file: The filepointer
        :type file: IO
        """
        self.read(file)

    def write_register(self, file: IO):
        """
        Function that writes the register, if it was succesfully read.

        :param file: The filepointer
        :type file: IO
        """
        self.write(file)

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
        return len([d for d in self.__data if d is not None]) == 0
