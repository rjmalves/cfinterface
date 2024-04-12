from typing import TypeVar, Type, Generator, Optional, Union, List

from cfinterface.components.register import Register


class RegisterData:
    """
    Class for a storing, managing and accessing data for a register file.
    """

    __slots__ = ["__root", "__head"]

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
        else:
            if before.previous:
                before.previous.next = new
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
        else:
            after.next.previous = new
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

    def get_registers_of_type(
        self, t: Type[T], **kwargs
    ) -> Optional[Union[T, List[T]]]:
        """
        A register or register list that only returns
        registers of type T that meet
        given filter requirements passed as kwargs.

        :param t: The register type that is desired
        :type t: Type[T]
        :return: Registers filtered by type T and optional properties
        :rtype: T | list[T] | None
        """

        def __meets(r) -> bool:
            conditions: List[bool] = []
            for k, v in kwargs.items():
                if v is not None:
                    conditions.append(getattr(r, k) == v)
            return all(conditions)

        all_registers_of_type = [b for b in self.of_type(t)]
        filtered_registers = [r for r in all_registers_of_type if __meets(r)]
        if len(filtered_registers) == 0:
            return None
        elif len(filtered_registers) == 1:
            return filtered_registers[0]
        else:
            return filtered_registers

    def remove_registers_of_type(self, t: Type[T], **kwargs):
        """
        Removes a set of registers given a type and an optional group of
        filters, similar to `get_registers_of_type()`

        :param t: The register type that is desired
        :type t: Type[T]
        """
        filtered_registers = self.get_registers_of_type(t, **kwargs)
        if isinstance(filtered_registers, t) and isinstance(
            filtered_registers, Register
        ):
            self.remove(filtered_registers)
        elif isinstance(filtered_registers, list):
            for r in filtered_registers:
                if isinstance(r, Register) and r != self.__root:
                    self.remove(r)

    @property
    def first(self) -> Register:
        return self.__root

    @property
    def last(self) -> Register:
        return self.__head
