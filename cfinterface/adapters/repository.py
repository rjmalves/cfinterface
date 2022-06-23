from typing import List, Optional, Any
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
    def read(self, line: Any) -> List[Any]:
        """
        Reads a line for extracting information following
        the given fields.

        :param line: The line to be read
        :type line: Any
        :return: The extracted values, in order
        :rtype: List[Any]
        """
        raise NotImplementedError

    @abstractmethod
    def write(self, values: List[Any]) -> Any:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of the fields to be written
        :type line: List[Any]
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
