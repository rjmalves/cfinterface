from typing import IO, Any

from cfinterface.components.section import Section


class DefaultSection(Section):
    """
    A class for representing a default section, which contains no data
    and is used for representing empty data.
    """

    __slots__ = []

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DefaultSection):
            return False
        return bool(self.data == o.data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        self.data = file.readline()
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        if len(self.data) > 0:
            file.write(self.data)
        return True
