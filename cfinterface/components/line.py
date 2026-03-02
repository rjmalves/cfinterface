from typing import Any, cast, overload

from cfinterface.adapters.components.line.repository import (
    factory,
)
from cfinterface.components.field import Field
from cfinterface.storage import StorageType


class Line:
    """
    Class for representing a generic line that is composed
    of fields and can be read from or written to a file.
    """

    __slots__ = [
        "_delimiter",
        "_fields",
        "_values",
        "_storage",
        "_repository",
        "_size",
    ]

    def __init__(
        self,
        fields: list[Field],
        values: list[Any] | None = None,
        delimiter: str | bytes | None = None,
        storage: str | StorageType = "",
    ):
        self._delimiter = delimiter
        self._fields = fields
        self._values = values
        self._storage = storage
        self.__generate_repository()
        self._size = sum([f.size for f in fields])

    def __generate_repository(self) -> None:
        self._repository = factory(self._storage)(self._fields, self._values)

    @overload
    def read(self, line: str) -> list[Any]: ...

    @overload
    def read(self, line: bytes) -> list[Any]: ...

    def read(self, line: str | bytes) -> list[Any]:
        return self._repository.read(line, self._delimiter)

    def write(self, values: list[Any]) -> str | bytes:
        return cast(
            str | bytes, self._repository.write(values, self._delimiter)
        )

    @property
    def fields(self) -> list[Field]:
        return self._repository.fields

    @fields.setter
    def fields(self, vals: list[Field]) -> None:
        self._repository.fields = vals

    @property
    def values(self) -> list[Any]:
        return self._repository.values

    @values.setter
    def values(self, vals: list[Any]) -> None:
        self._repository.values = vals

    @property
    def delimiter(self) -> str | bytes | None:
        return self._delimiter

    @delimiter.setter
    def delimiter(self, d: str | bytes | None) -> None:
        self._delimiter = d

    @property
    def storage(self) -> str | StorageType:
        return self._storage

    @storage.setter
    def storage(self, s: str | StorageType) -> None:
        self._storage = s
        self.__generate_repository()

    @property
    def size(self) -> int:
        return self._size
