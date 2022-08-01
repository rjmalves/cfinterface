from typing import List, Any

from cfinterface.adapters.line.repository import Repository


class PositionalRepository(Repository):

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
        for field in self._fields:
            field.read(line)
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
        line = ""
        self.values = values
        for field in self._fields:
            line = field.write(line)
        return line + "\n"
