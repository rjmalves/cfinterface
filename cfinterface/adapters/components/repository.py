import re
from abc import ABC, abstractmethod
from typing import IO, Any, Literal, Union, overload

from cfinterface.storage import StorageType

_pattern_cache: dict[str | bytes, "re.Pattern[Any]"] = {}


def _compile(pattern: str | bytes) -> "re.Pattern[Any]":
    compiled = _pattern_cache.get(pattern)
    if compiled is None:
        compiled = re.compile(pattern)
        _pattern_cache[pattern] = compiled
    return compiled


class Repository(ABC):
    @staticmethod
    @abstractmethod
    def matches(pattern: str | bytes, line: str | bytes) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def begins(pattern: str | bytes, line: str | bytes) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def ends(pattern: str | bytes, line: str | bytes) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def read(file: IO[Any], linesize: int) -> str | bytes:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def write(file: IO[Any], data: str | bytes) -> int:
        raise NotImplementedError


class BinaryRepository(Repository):
    @staticmethod
    def matches(pattern: str | bytes, line: str | bytes) -> bool:
        line_bytes = line if isinstance(line, bytes) else line.encode("utf-8")
        if isinstance(pattern, bytes):
            return _compile(pattern).search(line_bytes) is not None
        return _compile(pattern).search(line_bytes.decode("utf-8")) is not None

    @staticmethod
    def begins(pattern: str | bytes, line: str | bytes) -> bool:
        line_bytes = line if isinstance(line, bytes) else line.encode("utf-8")
        pat_bytes = (
            pattern if isinstance(pattern, bytes) else pattern.encode("utf-8")
        )
        return _compile(pat_bytes).search(line_bytes) is not None

    @staticmethod
    def ends(pattern: str | bytes, line: str | bytes) -> bool:
        line_bytes = line if isinstance(line, bytes) else line.encode("utf-8")
        pat_bytes = (
            pattern if isinstance(pattern, bytes) else pattern.encode("utf-8")
        )
        return _compile(pat_bytes).search(line_bytes) is not None

    @staticmethod
    def read(file: IO[Any], linesize: int) -> bytes:
        return file.read(linesize)  # type: ignore[no-any-return]

    @staticmethod
    def write(file: IO[Any], data: str | bytes) -> int:
        return file.write(data)  # type: ignore[no-any-return]


class TextualRepository(Repository):
    @staticmethod
    def matches(pattern: str | bytes, line: str | bytes) -> bool:
        line_str = line if isinstance(line, str) else line.decode("utf-8")
        pat_str = (
            pattern if isinstance(pattern, str) else pattern.decode("utf-8")
        )
        return _compile(pat_str).search(line_str) is not None

    @staticmethod
    def begins(pattern: str | bytes, line: str | bytes) -> bool:
        line_str = line if isinstance(line, str) else line.decode("utf-8")
        pat_str = (
            pattern if isinstance(pattern, str) else pattern.decode("utf-8")
        )
        return _compile(pat_str).search(line_str) is not None

    @staticmethod
    def ends(pattern: str | bytes, line: str | bytes) -> bool:
        line_str = line if isinstance(line, str) else line.decode("utf-8")
        pat_str = (
            pattern if isinstance(pattern, str) else pattern.decode("utf-8")
        )
        return _compile(pat_str).search(line_str) is not None

    @staticmethod
    def read(file: IO[Any], linesize: int) -> str:
        return file.readline()  # type: ignore[no-any-return]

    @staticmethod
    def write(file: IO[Any], data: str | bytes) -> int:
        return file.write(data)  # type: ignore[no-any-return]


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
