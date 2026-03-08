from __future__ import annotations

from typing import IO, Any, overload

from cfinterface.adapters.components.repository import factory
from cfinterface.storage import StorageType


class Block:
    """
    Class for a generic block in a textfile, with given markers
    for beginning and end and reading states.
    """

    __slots__ = [
        "__data",
        "_container",
        "_index",
        "__previous_fallback",
        "__next_fallback",
    ]

    BEGIN_PATTERN: str | bytes = ""
    END_PATTERN: str | bytes = ""
    MAX_LINES = 10000

    def __init__(
        self,
        previous: Any | None = None,
        next: Any | None = None,
        data: Any | None = None,
    ) -> None:
        self._container = None
        self._index = 0
        self.__previous_fallback = previous
        self.__next_fallback = next
        self.__data: Any = data

    def __eq__(self, o: object) -> bool:
        raise NotImplementedError

    @classmethod
    @overload
    def begins(cls, line: str, storage: str | StorageType = "") -> bool: ...

    @classmethod
    @overload
    def begins(cls, line: bytes, storage: str | StorageType = "") -> bool: ...

    @classmethod
    def begins(cls, line: str | bytes, storage: str | StorageType = "") -> bool:
        return factory(storage).begins(cls.BEGIN_PATTERN, line)

    @classmethod
    @overload
    def ends(cls, line: str, storage: str | StorageType = "") -> bool: ...

    @classmethod
    @overload
    def ends(cls, line: bytes, storage: str | StorageType = "") -> bool: ...

    @classmethod
    def ends(cls, line: str | bytes, storage: str | StorageType = "") -> bool:
        return factory(storage).ends(cls.END_PATTERN, line)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError

    def read_block(self, file: IO[Any], *args: Any, **kwargs: Any) -> None:
        self.read(file, *args, **kwargs)

    def write_block(self, file: IO[Any], *args: Any, **kwargs: Any) -> None:
        self.write(file, *args, **kwargs)

    @property
    def previous(self) -> Block | None:
        if self._container is not None:
            if self._index == 0:
                return None
            return self._container._items[self._index - 1]
        return self.__previous_fallback

    @previous.setter
    def previous(self, b: Block) -> None:
        self.__previous_fallback = b

    @property
    def next(self) -> Block | None:
        if self._container is not None:
            if self._index >= len(self._container._items) - 1:
                return None
            return self._container._items[self._index + 1]
        return self.__next_fallback

    @next.setter
    def next(self, b: Block) -> None:
        self.__next_fallback = b

    @property
    def data(self) -> Any:
        return self.__data

    @data.setter
    def data(self, d: Any) -> None:
        self.__data = d

    @property
    def is_first(self) -> bool:
        if self._container is not None:
            return self._index == 0
        return self.__previous_fallback is None

    @property
    def is_last(self) -> bool:
        if self._container is not None:
            return self._index == len(self._container._items) - 1
        return self.__next_fallback is None

    @property
    def empty(self) -> bool:
        return self.__data is None
