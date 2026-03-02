from abc import ABC, abstractmethod
from io import BytesIO, StringIO
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
    __slots__ = ["_content", "_wrap_io"]

    def __init__(
        self, content: str | bytes, wrap_io: bool = False, *args: Any
    ) -> None:
        self._content = content
        self._wrap_io = wrap_io

    def __enter__(self) -> "Repository":
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: B027
        pass

    @abstractmethod
    def read(self, n: int) -> str | bytes:
        raise NotImplementedError

    @property
    @abstractmethod
    def file(self) -> IO[Any]:
        raise NotImplementedError


class BinaryRepository(Repository):
    __slots__ = ["_filepointer"]

    def __init__(
        self, content: str | bytes, wrap_io: bool = False, *args: Any
    ) -> None:
        super().__init__(content, wrap_io)
        self._filepointer: BinaryIO = None  # type: ignore[assignment]

    def __enter__(self) -> "BinaryRepository":
        self._filepointer = (
            BytesIO(self._content)  # type: ignore[arg-type]
            if self._wrap_io
            else open(self._content, "rb")  # type: ignore[arg-type]
        )
        super().__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        super().__exit__(*args)
        self._filepointer.close()

    def read(self, n: int) -> bytes:
        return self._filepointer.read(n)

    @property
    def file(self) -> BinaryIO:
        return self._filepointer


class TextualRepository(Repository):
    __slots__ = ["_filepointer", "_encoding"]

    def __init__(
        self,
        content: str,
        wrap_io: bool = False,
        encoding: str = "utf-8",
        *args: Any,
    ) -> None:
        super().__init__(content, wrap_io)
        self._encoding = encoding
        self._filepointer: TextIO = None  # type: ignore[assignment]

    def __enter__(self) -> "TextualRepository":
        self._filepointer = (
            StringIO(self._content)  # type: ignore[arg-type]
            if self._wrap_io
            else open(self._content, encoding=self._encoding)  # type: ignore[arg-type]
        )
        super().__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        super().__exit__(*args)
        self._filepointer.close()

    def read(self, n: int) -> str:
        return self._filepointer.readline()

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
