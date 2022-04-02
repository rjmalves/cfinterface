from typing import List, TypeVar, Type, Generator

from cfi.components.block import Block


class BlockData:
    """
    Class for a storing, managing and accessing data for a block file.
    """

    T = TypeVar("T")

    def __init__(self, root: Block) -> None:
        self.__root = root

    def __iter__(self):
        def traverse(current: Block) -> Block:
            if current.next:
                for b in traverse(b):
                    yield b

        for b in traverse(self.__root):
            yield b

    def add(self, after: Block, new: Block):
        pass

    def remove(self, b: Block):
        pass

    # This has to be a generator only for blocks of type T
    def of_type(self, t: Type[T]) -> Generator[T]:
        pass
