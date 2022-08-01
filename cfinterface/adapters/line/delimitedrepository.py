from typing import List, Any, Optional

from cfinterface.components.field import Field
from cfinterface.adapters.line.repository import Repository


class DelimitedRepository(Repository):
    def __init__(
        self,
        fields: List[Field],
        values: Optional[List[Any]] = None,
        delimiter: str = ";",
    ) -> None:
        self._delimter = delimiter
        self._fields = [
            DelimitedRepository.__positional_to_delimited_field(f)
            for f in fields
        ]
        if values is not None:
            for f, v in zip(self._fields, values):
                f.value = v

    @staticmethod
    def __positional_to_delimited_field(f: Field) -> Field:
        f.ending_position = f.size
        f.starting_position = 0
        return f

    # Override
    def read(self, line: str) -> List[Any]:
        """
        Reads a line for extracting information following
        the given fields.

        :param line: The line to be read
        :type line: str
        :return: The extracted values, in order
        :rtype: List[Any]
        """
        values = [v.strip() for v in line.split(self._delimter)]
        for field, value in zip(self._fields, values):
            field.read(value)
        return self.values

    # Override
    def write(self, values: List[Any]) -> str:
        """
        Writes to a line with the existing information
        in the given fields.

        :param values: The value of the fields to be written
        :type line: List[Any]
        :return: The line with the new field information
        :rtype: str
        """
        self.values = values
        separated = [field.write("").strip() for field in self._fields]
        return self._delimter.join(separated) + "\n"
