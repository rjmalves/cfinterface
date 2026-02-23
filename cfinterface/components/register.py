from typing import Any, IO, Union, List
from cfinterface.components.field import Field
import inspect
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.line import Line
from cfinterface.storage import StorageType

from cfinterface.adapters.components.repository import factory


class Register:
    """
    Class for a generic register in a textfile, with a given identifier
    which is located at the beginning of the line.
    """

    __slots__ = [
        "__data",
        "__identifier_field",
        "_container",
        "_index",
        "__previous_fallback",
        "__next_fallback",
    ]

    IDENTIFIER: Union[str, bytes] = ""
    IDENTIFIER_DIGITS = 0
    LINE = Line([])
    _REGISTER_PROPERTIES = [
        "data",
        "empty",
        "is_first",
        "is_last",
        "next",
        "previous",
        "custom_properties",
    ]

    def __init__(
        self,
        previous=None,
        next=None,
        data=None,
    ) -> None:
        self.__identifier_field: Field = LiteralField(
            self.__class__.IDENTIFIER_DIGITS, 0
        )
        self._container = None
        self._index = 0
        self.__previous_fallback = previous
        self.__next_fallback = next
        if data is None:
            self.__data = [None] * len(self.__class__.LINE.fields)
        else:
            self.__data = data

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return o.data == self.data

    @classmethod
    def matches(
        cls, line: Union[str, bytes], storage: Union[str, StorageType] = ""
    ):
        return factory(storage).matches(
            cls.IDENTIFIER, line[: cls.IDENTIFIER_DIGITS]
        )

    def read(
        self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs
    ) -> bool:
        line = Line(
            [self.__identifier_field] + self.__class__.LINE.fields,
            delimiter=self.__class__.LINE.delimiter,
            storage=storage,
        )
        self.data = line.read(
            factory(storage).read(file, self.IDENTIFIER_DIGITS + line.size)
        )[1:]
        return True

    def write(
        self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs
    ) -> bool:
        if not self.empty:
            line = Line(
                [self.__identifier_field] + self.__class__.LINE.fields,
                delimiter=self.__class__.LINE.delimiter,
                storage=storage,
            )
            linedata = line.write([self.__class__.IDENTIFIER] + self.data)
            factory(storage).write(file, linedata)
        return True

    def read_register(
        self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs
    ):
        self.read(file, storage, *args, **kwargs)

    def write_register(
        self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs
    ):
        self.write(file, storage, *args, **kwargs)

    @property
    def previous(self) -> "Register":
        if self._container is not None:
            if self._index == 0:
                return None
            return self._container._items[self._index - 1]
        return self.__previous_fallback

    @previous.setter
    def previous(self, b: "Register"):
        self.__previous_fallback = b

    @property
    def next(self) -> "Register":
        if self._container is not None:
            if self._index >= len(self._container._items) - 1:
                return None
            return self._container._items[self._index + 1]
        return self.__next_fallback

    @next.setter
    def next(self, b: "Register"):
        self.__next_fallback = b

    @property
    def data(self) -> Any:
        return self.__data

    @data.setter
    def data(self, d: Any):
        self.__data = d

    @property
    def is_first(self) -> bool:
        if self._container is not None:
            return self._index == 0
        return self.__previous_fallback is None

    @property
    def is_last(self) -> bool:
        if self._container is not None:
            return self._index == len(self._container._items) - 1
        return self.__next_fallback is None

    @property
    def empty(self) -> bool:
        return len([d for d in self.__data if d is not None]) == 0

    @property
    def custom_properties(self) -> List[str]:
        return [
            nome
            for (nome, _) in inspect.getmembers(
                self.__class__, lambda p: isinstance(p, property)
            )
            if nome not in Register._REGISTER_PROPERTIES
        ]
