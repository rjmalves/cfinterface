from typing import IO, BinaryIO, TextIO, Union, Dict, Type, overload
from typing import Literal
from abc import ABC, abstractmethod

from cfinterface.storage import StorageType


class Repository(ABC):
    __slots__ = ["_to", "_wrap_io"]

    def __init__(self, to: Union[str, IO], *args) -> None:
        self._to = to
        self._wrap_io = isinstance(to, str)

    def __enter__(self) -> "Repository":
        return self

    def __exit__(self, *args):
        pass

    @abstractmethod
    def write(self, data: Union[str, bytes]):
        raise NotImplementedError

    @property
    @abstractmethod
    def file(self) -> IO:
        raise NotImplementedError


class BinaryRepository(Repository):
    __slots__ = ["_filepointer"]

    def __init__(self, path: str, *args) -> None:
        super().__init__(path)
        self._filepointer: BinaryIO = None  # type: ignore

    def __enter__(self):
        self._filepointer = open(self._to, "wb") if self._wrap_io else self._to
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        if self._wrap_io:
            self._filepointer.close()

    def write(self, data: bytes):
        if isinstance(data, bytes):
            self._filepointer.write(data)

    @property
    def file(self) -> BinaryIO:
        return self._filepointer


class TextualRepository(Repository):
    __slots__ = ["_filepointer", "_encoding"]

    def __init__(self, path: str, encoding: str) -> None:
        super().__init__(path)
        self._filepointer: TextIO = None  # type: ignore
        self._encoding = encoding

    def __enter__(self):
        self._filepointer = (
            open(self._to, "w", encoding=self._encoding)
            if self._wrap_io
            else self._to
        )
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        if self._wrap_io:
            self._filepointer.close()

    def write(self, data: str):
        if isinstance(data, str):
            self._filepointer.write(data)

    @property
    def file(self) -> TextIO:
        return self._filepointer


@overload
def factory(kind: Literal["TEXT"]) -> Type[TextualRepository]: ...


@overload
def factory(kind: Literal["BINARY"]) -> Type[BinaryRepository]: ...


@overload
def factory(kind: Union[str, StorageType]) -> Type[Repository]: ...


def factory(kind: Union[str, "StorageType"]) -> Type[Repository]:
    mappings: Dict[Union[str, StorageType], Type[Repository]] = {
        StorageType.TEXT: TextualRepository,
        StorageType.BINARY: BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
