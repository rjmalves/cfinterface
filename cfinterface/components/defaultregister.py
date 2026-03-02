from typing import IO, Any

from cfinterface.components.register import Register
from cfinterface.storage import StorageType


class DefaultRegister(Register):
    """
    A class for representing a default register, which contains exactly
    the data from the read line. Mainly used for comments.
    """

    __slots__ = []

    def __init__(
        self,
        previous: Any | None = None,
        next: Any | None = None,
        data: Any | None = None,
    ) -> None:
        super().__init__(previous, next, data)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DefaultRegister):
            return False
        return bool(self.data == o.data)

    def read(
        self,
        file: IO[Any],
        storage: str | StorageType = "",
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        if storage != StorageType.BINARY:
            self.data = file.readline()
        else:
            self.data = None
        return True

    def write(
        self,
        file: IO[Any],
        storage: str | StorageType = "",
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        if storage != StorageType.BINARY:
            file.write(self.data)
        return True
