from typing import Union, Dict, Type, IO, Any, overload
import re
from abc import ABC, abstractmethod
from typing import Literal

from cfinterface.storage import StorageType

_pattern_cache: Dict[Union[str, bytes], "re.Pattern[Any]"] = {}


def _compile(pattern: Union[str, bytes]) -> "re.Pattern[Any]":
    compiled = _pattern_cache.get(pattern)
    if compiled is None:
        compiled = re.compile(pattern)
        _pattern_cache[pattern] = compiled
    return compiled


class Repository(ABC):
    @staticmethod
    @abstractmethod
    def matches(pattern: Union[str, bytes], line: Union[str, bytes]) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def begins(pattern: Union[str, bytes], line: Union[str, bytes]) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def ends(pattern: Union[str, bytes], line: Union[str, bytes]) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def read(file: IO, linesize: int) -> Union[str, bytes]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def write(file: IO, data: Union[str, bytes]) -> int:
        raise NotImplementedError


class BinaryRepository(Repository):
    @staticmethod
    def matches(pattern: Union[str, bytes], line: bytes) -> bool:
        if isinstance(pattern, bytes):
            return _compile(pattern).search(line) is not None
        return _compile(pattern).search(line.decode("utf-8")) is not None

    @staticmethod
    def begins(pattern: bytes, line: bytes) -> bool:
        return _compile(pattern).search(line) is not None

    @staticmethod
    def ends(pattern: bytes, line: bytes) -> bool:
        return _compile(pattern).search(line) is not None

    @staticmethod
    def read(file: IO, linesize: int) -> bytes:
        return file.read(linesize)

    @staticmethod
    def write(file: IO, data: bytes) -> int:
        return file.write(data)


class TextualRepository(Repository):
    @staticmethod
    def matches(pattern: str, line: str) -> bool:
        return _compile(pattern).search(line) is not None

    @staticmethod
    def begins(pattern: str, line: str) -> bool:
        return _compile(pattern).search(line) is not None

    @staticmethod
    def ends(pattern: str, line: str) -> bool:
        return _compile(pattern).search(line) is not None

    @staticmethod
    def read(file: IO, linesize: int) -> str:
        return file.readline()

    @staticmethod
    def write(file: IO, data: str) -> int:
        return file.write(data)


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
