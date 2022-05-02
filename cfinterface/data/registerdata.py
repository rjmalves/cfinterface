from typing import TypeVar, Type, Generator

from cfinterface.components.register import Register


class RegisterData:
    """
    Class for a storing, managing and accessing data for a register file.
    """

    T = TypeVar("T")

    def __init__(self, root: Register) -> None:
        self.__root = root
        self.__head = root

    def __iter__(self):
        current = self.__root
        while current:
            yield current
            current = current.next

    def __len__(self) -> int:
        count = 0
        for _ in self:
            count += 1
        return count

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RegisterData):
            return False
        rd: RegisterData = o
        if len(self) != len(rd):
            return False
        for r1, r2 in zip(self, rd):
            if r1 != r2:
                return False
        return True

    def preppend(self, r: Register):
        """
        Appends a register to the beginning of the data.

        :param r: The new register to preppended to the data.
        :type r: Register
        """
        self.add_before(self.__root, r)

    def append(self, r: Register):
        """
        Appends a register to the end of the data.

        :param r: The new register to append to the data
        :type r: Register
        """
        self.add_after(self.__head, r)

    def add_before(self, before: Register, new: Register):
        """
        Adds a new register to the data before another
        specified register.

        :param before: The existing register which will be preppended
        :type before: Register
        :param new: The new register to add to the data
        :type new: Register
        """
        if before == self.__root:
            self.__root = new
        new.previous = before.previous
        before.previous = new
        new.next = before

    def add_after(self, after: Register, new: Register):
        """
        Adds a new register to the data after another
        specified register.

        :param after: The existing register which will be appended
        :type after: Register
        :param new: The new register to add to the data
        :type new: Register
        """
        if after == self.__head:
            self.__head = new
        new.next = after.next
        after.next = new
        new.previous = after

    def remove(self, r: Register):
        """
        Removes an existing register in the chain.

        :param r: The register to be removed
        :type r: Register
        """
        if r.previous is not None:
            r.previous.next = r.next
        if r.next is not None:
            r.next.previous = r.previous

    def of_type(self, t: Type[T]) -> Generator[T, None, None]:
        """
        A register generator that only returns registers of type T.

        :param t: The register type that is desired
        :type t: Type[T]
        :yield: Registers filtered by type T
        :rtype: Generator[T, None, None]
        """
        for r in self:
            if isinstance(r, t):
                yield r

    @property
    def first(self) -> Register:
        return self.__root

    @property
    def last(self) -> Register:
        return self.__head
