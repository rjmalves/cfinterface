from typing import IO, Any

from cfinterface.components.block import Block


class DefaultBlock(Block):
    """
    A class for representing a default block, which contains exactly
    the data from the read line. Mainly used for comments.
    """

    __slots__ = []

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DefaultBlock):
            return False
        return bool(self.data == o.data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        self.data = file.readline()
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        if len(self.data) > 0:
            file.write(self.data)
        return True
