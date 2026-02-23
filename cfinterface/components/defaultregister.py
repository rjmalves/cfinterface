from typing import IO, Union
from cfinterface.components.register import Register
from cfinterface.storage import StorageType


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

    def read(
        self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs
    ) -> bool:
        if storage != StorageType.BINARY:
            self.data = file.readline()
        else:
            self.data = None
        return True

    def write(
        self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs
    ) -> bool:
        if storage != StorageType.BINARY:
            file.write(self.data)
        return True
