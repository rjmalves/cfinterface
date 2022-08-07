from typing import IO
from cfinterface.components.register import Register


class DefaultRegister(Register):
    """
    A class for representing a default register, which contains exactly
    the data from the read line. Mainly used for comments.
    """

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DefaultRegister):
            return False
        return self.data == o.data

    def read(self, file: IO, storage: str = "") -> bool:
        self.data = file.readline()
        return True

    def write(self, file: IO, storage: str = "") -> bool:
        file.write(self.data)
        return True
