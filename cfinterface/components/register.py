from typing import Any, IO, Union, List
from cfinterface.components.field import Field
import inspect
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.line import Line


from cfinterface.adapters.components.repository import factory


class Register:
    """
    Class for a generic register in a textfile, with a given identifier
    which is located at the beginning of the line.
    """

    __slots__ = ["__previous", "__next", "__data", "__identifier_field"]

    IDENTIFIER: Union[str, bytes] = ""
    IDENTIFIER_DIGITS = 0
    LINE = Line([])
    _REGISTER_PROPERTIES = [
        "data",
        "empty",
        "is_first",
        "is_last",
        "next",
        "previous",
        "custom_properties",
    ]

    def __init__(
        self,
        previous=None,
        next=None,
        data=None,
    ) -> None:
        self.__identifier_field: Field = LiteralField(
            self.__class__.IDENTIFIER_DIGITS, 0
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
    def matches(cls, line: Union[str, bytes], storage: str = ""):
        """
        Checks if the current line matches the identifier of the register.

        :param line: The candidate line for containing
            the register information
        :type line: str | bytes
        """
        return factory(storage).matches(
            cls.IDENTIFIER, line[: cls.IDENTIFIER_DIGITS]
        )

    def read(self, file: IO, storage: str = "", *args, **kwargs) -> bool:
        """
        Generic function to perform the reading of the register using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the reading
        :rtype: bool
        """
        line = Line(
            [self.__identifier_field] + self.__class__.LINE.fields,
            delimiter=self.__class__.LINE.delimiter,
            storage=storage,
        )
        self.data = line.read(
            factory(storage).read(file, self.IDENTIFIER_DIGITS + line.size)
        )[1:]
        return True

    def write(self, file: IO, storage: str = "", *args, **kwargs) -> bool:
        """
        Generic function to perform the writing of the register using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the writing
        :rtype: bool
        """
        if not self.empty:
            line = Line(
                [self.__identifier_field] + self.__class__.LINE.fields,
                delimiter=self.__class__.LINE.delimiter,
                storage=storage,
            )
            linedata = line.write([self.__class__.IDENTIFIER] + self.data)
            factory(storage).write(file, linedata)
        return True

    def read_register(self, file: IO, storage: str = "", *args, **kwargs):
        """
        Function that reads the register and evaluates the result.

        :param file: The filepointer
        :type file: IO
        """
        self.read(file, storage, *args, **kwargs)

    def write_register(self, file: IO, storage: str = "", *args, **kwargs):
        """
        Function that writes the register, if it was succesfully read.

        :param file: The filepointer
        :type file: IO
        """
        self.write(file, storage, *args, **kwargs)

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

    @property
    def custom_properties(self) -> List[str]:
        return [
            nome
            for (nome, _) in inspect.getmembers(
                self.__class__, lambda p: isinstance(p, property)
            )
            if nome not in Register._REGISTER_PROPERTIES
        ]
