from abc import ABC, abstractmethod
from typing import (
    IO,
    Any,
    BinaryIO,
    Literal,
    TextIO,
    Union,
    overload,
)

from cfinterface.storage import StorageType


class Repository(ABC):
    __slots__ = ["_to", "_wrap_io"]

    def __init__(self, to: str | IO[Any], *args: Any) -> None:
        self._to = to
        self._wrap_io = isinstance(to, str)

    def __enter__(self) -> "Repository":
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: B027
        pass

    @abstractmethod
    def write(self, data: str | bytes) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def file(self) -> IO[Any]:
        raise NotImplementedError


class BinaryRepository(Repository):
    __slots__ = ["_filepointer"]

    def __init__(self, path: str | IO[Any], *args: Any) -> None:
        super().__init__(path)
        self._filepointer: BinaryIO = None  # type: ignore[assignment]

    def __enter__(self) -> "BinaryRepository":
        self._filepointer = (
            open(self._to, "wb")  # type: ignore[arg-type]
            if self._wrap_io
            else self._to  # type: ignore[assignment]
        )
        super().__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        super().__exit__(*args)
        if self._wrap_io:
            self._filepointer.close()

    def write(self, data: str | bytes) -> None:
        if isinstance(data, bytes):
            self._filepointer.write(data)

    @property
    def file(self) -> BinaryIO:
        return self._filepointer


class TextualRepository(Repository):
    __slots__ = ["_filepointer", "_encoding"]

    def __init__(self, path: str | IO[Any], encoding: str = "utf-8") -> None:
        super().__init__(path)
        self._filepointer: TextIO = None  # type: ignore[assignment]
        self._encoding = encoding

    def __enter__(self) -> "TextualRepository":
        self._filepointer = (
            open(self._to, "w", encoding=self._encoding)  # type: ignore[arg-type]
            if self._wrap_io
            else self._to  # type: ignore[assignment]
        )
        super().__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        super().__exit__(*args)
        if self._wrap_io:
            self._filepointer.close()

    def write(self, data: str | bytes) -> None:
        if isinstance(data, str):
            self._filepointer.write(data)

    @property
    def file(self) -> TextIO:
        return self._filepointer


@overload
def factory(kind: Literal["TEXT"]) -> type[TextualRepository]: ...


@overload
def factory(kind: Literal["BINARY"]) -> type[BinaryRepository]: ...


@overload
def factory(kind: str | StorageType) -> type[Repository]: ...


def factory(kind: Union[str, "StorageType"]) -> type[Repository]:
    mappings: dict[str | StorageType, type[Repository]] = {
        StorageType.TEXT: TextualRepository,
        StorageType.BINARY: BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
