from typing import List, Optional, Any, Type, Union, Dict, overload
from typing import Literal
from abc import ABC, abstractmethod

from cfinterface.components.field import Field
from cfinterface.storage import StorageType


class Repository(ABC):
    def __init__(
        self, fields: List[Field], values: Optional[List[Any]] = None
    ) -> None:
        self._fields = fields
        if values is not None:
            for f, v in zip(self._fields, values):
                f.value = v

    @abstractmethod
    def read(
        self, line: Any, delimiter: Optional[Union[str, bytes]]
    ) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def write(
        self, values: List[Any], delimiter: Optional[Union[str, bytes]]
    ) -> Any:
        raise NotImplementedError

    @property
    def fields(self) -> List[Field]:
        return self._fields

    @fields.setter
    def fields(self, f: List[Field]):
        self._fields = f

    @property
    def values(self) -> List[Any]:
        return [f.value for f in self._fields]

    @values.setter
    def values(self, vals: List[Any]):
        for f, v in zip(self._fields, vals):
            f.value = v


class TextualRepository(Repository):
    def __positional_to_delimited_field(self, f: Field) -> Field:
        f.ending_position = f.size
        f.starting_position = 0
        return f

    def __positional_reading(self, line: str) -> List[Any]:
        for field in self._fields:
            field.read(line)
        return self.values

    def __delimted_reading(self, line: str, delimiter: str) -> List[Any]:
        fields = [self.__positional_to_delimited_field(f) for f in self._fields]
        values = [v.strip() for v in line.split(delimiter)]
        for field, value in zip(fields, values):
            field.read(value)
        return self.values

    def read(
        self,
        line: str,
        delimiter: Optional[str] = None,
    ) -> List[Any]:
        if isinstance(delimiter, str):
            return self.__delimted_reading(line, delimiter)
        return self.__positional_reading(line)

    def __positional_writing(self, values: List[Any]) -> str:
        line = ""
        self.values = values
        for field in self._fields:
            line = field.write(line)
        return line + "\n"

    def __delimted_writing(self, values: List[Any], delimiter: str) -> str:
        fields = [self.__positional_to_delimited_field(f) for f in self._fields]
        self.values = values
        separated = [field.write("").strip() for field in fields]
        return delimiter.join(separated) + "\n"

    def write(self, values: List[Any], delimiter: Optional[str] = None) -> str:
        if isinstance(delimiter, str):
            return self.__delimted_writing(values, delimiter)
        return self.__positional_writing(values)


class BinaryRepository(Repository):
    def read(
        self,
        line: bytes,
        delimiter: Optional[bytes] = None,
    ) -> List[Any]:
        for field in self._fields:
            field.read(line)  # type: ignore
        return self.values

    def write(
        self, values: List[Any], delimiter: Optional[bytes] = None
    ) -> bytes:
        line = b""
        self.values = values
        for field in self._fields:
            line = field.write(line)
        return line


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
