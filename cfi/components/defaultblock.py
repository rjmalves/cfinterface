from typing import IO
from cfi.components.block import Block


class DefaultBlock(Block):
    """
    A class for representing a default block, which contains exactly
    the data from the read line. Mainly used for comments.
    """

    def read(self, file: IO) -> bool:
        self.data = file.readline()
        return True

    def write(self, file: IO) -> bool:
        file.write(self.data)
        return True
