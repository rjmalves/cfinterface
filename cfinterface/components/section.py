from typing import Any, IO


class Section:
    """
    Class for a generic section in a textfile, which begins and ends in
    a given order
    """

    __slots__ = ["__previous", "__next", "__data"]

    STORAGE: str = "TEXT"

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
        raise NotImplementedError()

    def read(self, file: IO, *args, **kwargs) -> bool:
        """
        Generic function to perform the reading of the section using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the reading
        :rtype: bool
        """
        raise NotImplementedError

    def write(self, file: IO, *args, **kwargs) -> bool:
        """
        Generic function to perform the writing of the section using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the writing
        :rtype: bool
        """
        raise NotImplementedError

    def read_section(self, file: IO, *args, **kwargs):
        """
        Function that reads the section and evaluates the result.

        :param file: The filepointer
        :type file: IO
        """
        self.read(file, *args, **kwargs)

    def write_section(self, file: IO, *args, **kwargs):
        """
        Function that writes the section, if it was succesfully read.

        :param file: The filepointer
        :type file: IO
        """
        self.write(file, *args, **kwargs)

    @property
    def previous(self) -> "Section":
        return self.__previous

    @previous.setter
    def previous(self, b: "Section"):
        self.__previous = b

    @property
    def next(self) -> "Section":
        return self.__next

    @next.setter
    def next(self, b: "Section"):
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
