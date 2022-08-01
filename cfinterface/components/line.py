from typing import Any, List, Optional

from cfinterface.components.field import Field

from cfinterface.adapters.line.repository import Repository
from cfinterface.adapters.line.positionalrepository import PositionalRepository
from cfinterface.adapters.line.delimitedrepository import DelimitedRepository


class Line:
    """
    Class for representing a generic line that is composed
    of fields and can be read from or written to a file.
    """

    def __init__(
        self,
        fields: List[Field],
        values: Optional[List[Any]] = None,
        delimiter: Optional[str] = None,
    ):
        self._delimiter = delimiter
        self._repository: Repository = None  # type: ignore
        if delimiter is None:
            self._repository = PositionalRepository(fields, values)
        else:
            self._repository = DelimitedRepository(fields, values, delimiter)

    def read(self, line: str) -> List[Any]:
        """
        Reads a line for extracting information following
        the given fields.

        :param line: The line to be read
        :type line: str
        :return: The extracted values, in order
        :rtype: List[Any]
        """
        return self._repository.read(line)

    def write(self, values: List[Any]) -> str:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of the fields to be written
        :type line: List[Any]
        :return: The line with the new field information
        :rtype: str
        """
        return self._repository.write(values)

    @property
    def fields(self) -> List[Field]:
        return self._repository.fields

    @fields.setter
    def fields(self, vals: List[Field]):
        self._repository.fields = vals

    @property
    def values(self) -> List[Any]:
        return self._repository.values

    @values.setter
    def values(self, vals: List[Any]):
        self._repository.values = vals

    @property
    def delimiter(self) -> Optional[str]:
        return self._delimiter

    @delimiter.setter
    def delimiter(self, d: Optional[str]):
        self._delimiter = d
