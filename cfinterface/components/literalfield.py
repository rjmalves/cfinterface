from typing import Optional, Union

from cfinterface.components.field import Field

from cfinterface.adapters.field.repository import Repository
from cfinterface.adapters.field.textualrepository import TextualRepository


class LiteralField(Field):
    """
    Class for representing an literal field for being read from and
    written to a file.
    """

    def __init__(
        self,
        size: int = 80,
        starting_position: int = 0,
        value: Optional[str] = None,
        interface: Repository = TextualRepository(),
    ) -> None:
        super().__init__(size, starting_position, value, interface)

    # Override
    def read(self, line: Union[str, bytes]) -> str:
        readline = self._interface.read(line)
        self._value = readline[
            self._starting_position : self._ending_position
        ].strip()
        return self._value

    # Override
    def write(self, line: Union[str, bytes]) -> Union[str, bytes]:
        if self.value is None:
            value = "".ljust(self._size)
        else:
            value = self.value
        return self._interface.write(
            value, line, self._starting_position, self._ending_position
        )

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, val: str):
        self._value = val
