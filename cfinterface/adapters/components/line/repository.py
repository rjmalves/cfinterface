from abc import ABC, abstractmethod
from typing import Any, Literal, Union, overload

from cfinterface.components.field import Field
from cfinterface.storage import StorageType


class Repository(ABC):
    def __init__(
        self, fields: list[Field], values: list[Any] | None = None
    ) -> None:
        self._fields = fields
        if values is not None:
            for f, v in zip(self._fields, values, strict=False):
                f.value = v

    @abstractmethod
    def read(self, line: Any, delimiter: str | bytes | None) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    def write(self, values: list[Any], delimiter: str | bytes | None) -> Any:
        raise NotImplementedError

    @property
    def fields(self) -> list[Field]:
        return self._fields

    @fields.setter
    def fields(self, f: list[Field]) -> None:
        self._fields = f

    @property
    def values(self) -> list[Any]:
        return [f.value for f in self._fields]

    @values.setter
    def values(self, vals: list[Any]) -> None:
        for f, v in zip(self._fields, vals, strict=False):
            f.value = v


class TextualRepository(Repository):
    def __positional_to_delimited_field(self, f: Field) -> Field:
        f.ending_position = f.size
        f.starting_position = 0
        return f

    def __positional_reading(self, line: str) -> list[Any]:
        for field in self._fields:
            field.read(line)
        return self.values

    def __delimted_reading(self, line: str, delimiter: str) -> list[Any]:
        fields = [self.__positional_to_delimited_field(f) for f in self._fields]
        values = [v.strip() for v in line.split(delimiter)]
        for field, value in zip(fields, values, strict=False):
            field.read(value)
        return self.values

    def read(
        self,
        line: Any,
        delimiter: str | bytes | None = None,
    ) -> list[Any]:
        line_str: str = line if isinstance(line, str) else line.decode("utf-8")
        if isinstance(delimiter, str):
            return self.__delimted_reading(line_str, delimiter)
        return self.__positional_reading(line_str)

    def __positional_writing(self, values: list[Any]) -> str:
        line = ""
        self.values = values
        for field in self._fields:
            line = field.write(line)
        return line + "\n"

    def __delimted_writing(self, values: list[Any], delimiter: str) -> str:
        fields = [self.__positional_to_delimited_field(f) for f in self._fields]
        self.values = values
        separated = [field.write("").strip() for field in fields]
        return delimiter.join(separated) + "\n"

    def write(
        self, values: list[Any], delimiter: str | bytes | None = None
    ) -> str:
        if isinstance(delimiter, str):
            return self.__delimted_writing(values, delimiter)
        return self.__positional_writing(values)


class BinaryRepository(Repository):
    def read(
        self,
        line: Any,
        delimiter: str | bytes | None = None,
    ) -> list[Any]:
        line_bytes: bytes = (
            line if isinstance(line, bytes) else line.encode("utf-8")
        )
        for field in self._fields:
            field.read(line_bytes)  # type: ignore[arg-type]
        return self.values

    def write(
        self, values: list[Any], delimiter: str | bytes | None = None
    ) -> bytes:
        line = b""
        self.values = values
        for field in self._fields:
            line = field.write(line)
        return line


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
