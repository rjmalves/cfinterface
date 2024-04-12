from typing import IO
from cfinterface.components.register import Register


class DefaultRegister(Register):
    """
    A class for representing a default register, which contains exactly
    the data from the read line. Mainly used for comments.
    """

    __slots__ = []

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DefaultRegister):
            return False
        return self.data == o.data

    def read(self, file: IO, storage: str = "", *args, **kwargs) -> bool:
        """
        Generic function to perform the reading of the register using
        a filepointer.

        :param file: The filepointer
        :type file: IO
        :return: The success, or not, in the reading
        :rtype: bool
        """
        if storage not in ["BINARY"]:
            self.data = file.readline()
        else:
            self.data = None
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
        if storage not in ["BINARY"]:
            file.write(self.data)
        return True
