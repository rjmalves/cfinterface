from typing import List, Optional, Any, Type, Union, Dict
from abc import ABC, abstractmethod

from cfinterface.components.field import Field


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
        """
        Reads a line for extracting information following
        the given fields.

        :param line: The line to be read
        :type line: Any
        :param delimiter: The (optional) delimiter of the line fields
        :type delimiter: str | bytes | None
        :return: The extracted values, in order
        :rtype: List[Any]
        """
        raise NotImplementedError

    @abstractmethod
    def write(
        self, values: List[Any], delimiter: Optional[Union[str, bytes]]
    ) -> Any:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of the fields to be written
        :type line: List[Any]
        :param delimiter: The (optional) delimiter of the line fields
        :type delimiter: str | bytes | None
        :return: The line with the new field information
        :rtype: Any
        """
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
        fields = [
            self.__positional_to_delimited_field(f) for f in self._fields
        ]
        values = [v.strip() for v in line.split(delimiter)]
        for field, value in zip(fields, values):
            field.read(value)
        return self.values

    # Override
    def read(
        self,
        line: Union[str, bytes],
        delimiter: Optional[Union[str, bytes]] = None,
    ) -> List[Any]:
        """
        Reads a line for extracting information following
        the given fields.

        :param line: The line to be read
        :type line: Union[str, bytes]
        :return: The extracted values, in order
        :rtype: List[Any]
        """
        if isinstance(line, str) and isinstance(delimiter, str):
            return self.__delimted_reading(line, delimiter)
        elif isinstance(line, str) and delimiter is None:
            return self.__positional_reading(line)
        return []

    def __positional_writing(self, values: List[Any]) -> str:
        line = ""
        self.values = values
        for field in self._fields:
            line = field.write(line)
        return line + "\n"

    def __delimted_writing(self, values: List[Any], delimiter: str) -> str:
        fields = [
            self.__positional_to_delimited_field(f) for f in self._fields
        ]
        self.values = values
        separated = [field.write("").strip() for field in fields]
        return delimiter.join(separated) + "\n"

    # Override
    def write(
        self, values: List[Any], delimiter: Optional[Union[str, bytes]] = None
    ) -> Union[str, bytes]:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of the fields to be written
        :type line: List[Any]
        :return: The line with the new field information
        :rtype: Union[str, bytes]
        """
        if isinstance(delimiter, str):
            return self.__delimted_writing(values, delimiter)
        else:
            return self.__positional_writing(values)


class BinaryRepository(Repository):

    # Override
    def read(
        self,
        line: Union[str, bytes],
        delimiter: Optional[Union[str, bytes]] = None,
    ) -> List[Any]:
        """
        Reads a line for extracting information following
        the given fields.

        :param line: The line to be read
        :type line: Union[str, bytes]
        :return: The extracted values, in order
        :rtype: List[Any]
        """
        for field in self._fields:
            field.read(line)  # type: ignore
        return self.values

    # Override
    def write(
        self, values: List[Any], delimiter: Optional[Union[str, bytes]] = None
    ) -> bytes:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of the fields to be written
        :type line: List[Any]
        :return: The line with the new field information
        :rtype: Union[str, bytes]
        """
        line = b""
        self.values = values
        for field in self._fields:
            line = field.write(line)
        return line


def factory(kind: str) -> Type[Repository]:
    mappings: Dict[str, Type[Repository]] = {
        "TEXT": TextualRepository,
        "BINARY": BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
