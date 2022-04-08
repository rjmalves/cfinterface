from typing import TypeVar, Type, Generator

from cfinterface.components.block import Block


class BlockData:
    """
    Class for a storing, managing and accessing data for a block file.
    """

    T = TypeVar("T")

    def __init__(self, root: Block) -> None:
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
        if not isinstance(o, BlockData):
            return False
        bd: BlockData = o
        if len(self) != len(bd):
            return False
        for b1, b2 in zip(self, bd):
            if b1 != b2:
                return False
        return True

    def preppend(self, b: Block):
        """
        Appends a block to the beginning of the data.

        :param b: The new block to preppended to the data.
        :type b: Block
        """
        self.add_before(self.__root, b)

    def append(self, b: Block):
        """
        Appends a block to the end of the data.

        :param b: The new block to append to the data
        :type b: Block
        """
        self.add_after(self.__head, b)

    def add_before(self, before: Block, new: Block):
        """
        Adds a new block to the data before another
        specified block.

        :param before: The existing block which will be preppended
        :type before: Block
        :param new: The new block to add to the data
        :type new: Block
        """
        if before == self.__root:
            self.__root = new
        new.previous = before.previous
        before.previous = new
        new.next = before

    def add_after(self, after: Block, new: Block):
        """
        Adds a new block to the data after another
        specified block.

        :param after: The existing block which will be appended
        :type after: Block
        :param new: The new block to add to the data
        :type new: Block
        """
        if after == self.__head:
            self.__head = new
        new.next = after.next
        after.next = new
        new.previous = after

    def remove(self, b: Block):
        """
        Removes an existing block in the chain.

        :param b: The block to be removed
        :type b: Block
        """
        if b.previous is not None:
            b.previous.next = b.next
        if b.next is not None:
            b.next.previous = b.previous

    def of_type(self, t: Type[T]) -> Generator[T, None, None]:
        """
        A block generator that only returns blocks of type T.

        :param t: The block type that is desired
        :type t: Type[T]
        :yield: Blocks filtered by type T
        :rtype: Generator[T, None, None]
        """
        for b in self:
            if isinstance(b, t):
                yield b

    @property
    def first(self) -> Block:
        return self.__root

    @property
    def last(self) -> Block:
        return self.__head
