from typing import Any, List, Optional

from cfinterface.components.field import Field


class Line:
    """
    Class for representing a generic line that is composed
    of fields and can be read from or written to a file.
    """

    def __init__(
        self, fields: List[Field], values: Optional[List[Any]] = None
    ):
        self._fields = fields
        if values is not None:
            for f, v in zip(self._fields, values):
                f.value = v

    def read(self, line: str) -> List[Any]:
        """
        Reads a line for extracting information following
        the given fields.

        :param line: The line to be read
        :type line: str
        :return: The extracted values, in order
        :rtype: List[Any]
        """
        for field in self._fields:
            field.read(line)
        return self.values

    def write(self, values: List[Any]) -> str:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of the fields to be written
        :type line: List[Any]
        :return: The line with the new field information
        :rtype: str
        """
        line = ""
        self.values = values
        for field in self._fields:
            line = field.write(line)
        return line + "\n"

    @property
    def values(self) -> List[Any]:
        return [f.value for f in self._fields]

    @values.setter
    def values(self, vals: List[Any]):
        for f, v in zip(self._fields, vals):
            f.value = v
