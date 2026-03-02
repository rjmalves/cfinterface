from collections.abc import Generator, Iterator
from typing import (
    Any,
    TypeVar,
    cast,
)

from cfinterface.components.register import Register

_T = TypeVar("_T")


class RegisterData:
    """
    Class for a storing, managing and accessing data for a register file.
    """

    __slots__ = ["_items", "_type_index"]

    def __init__(self, root: Register) -> None:
        self._items: list[Register] = [root]
        self._type_index: dict[type[Register], list[int]] = {type(root): [0]}
        self._refresh_indices(0)

    def __iter__(self) -> Iterator[Register]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, idx: int) -> Register:
        return self._items[idx]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RegisterData):
            return False
        if len(self) != len(o):
            return False
        return all(
            r1 == r2 for r1, r2 in zip(self._items, o._items, strict=False)
        )

    def _refresh_indices(self, start: int = 0) -> None:
        for i in range(start, len(self._items)):
            self._items[i]._container = self  # type: ignore[assignment]
            self._items[i]._index = i

    def _index_of(self, item: Register) -> int:
        for i, r in enumerate(self._items):
            if r is item:
                return i
        raise ValueError("Register not found in container")

    def _rebuild_type_index(self) -> None:
        self._type_index = {}
        for i, item in enumerate(self._items):
            t = type(item)
            if t not in self._type_index:
                self._type_index[t] = []
            self._type_index[t].append(i)

    def preppend(self, r: Register) -> None:
        """
        Appends a register to the beginning of the data.

        :param r: The new register to preppended to the data.
        :type r: Register
        """
        self._items.insert(0, r)
        self._refresh_indices(0)
        self._rebuild_type_index()

    def append(self, r: Register) -> None:
        """
        Appends a register to the end of the data.

        :param r: The new register to append to the data
        :type r: Register
        """
        self._items.append(r)
        self._refresh_indices(len(self._items) - 1)
        t = type(r)
        if t not in self._type_index:
            self._type_index[t] = []
        self._type_index[t].append(len(self._items) - 1)

    def add_before(self, before: Register, new: Register) -> None:
        """
        Adds a new register to the data before another
        specified register.

        :param before: The existing register which will be preppended
        :type before: Register
        :param new: The new register to add to the data
        :type new: Register
        """
        idx = self._index_of(before)
        self._items.insert(idx, new)
        self._refresh_indices(idx)
        self._rebuild_type_index()

    def add_after(self, after: Register, new: Register) -> None:
        """
        Adds a new register to the data after another
        specified register.

        :param after: The existing register which will be appended
        :type after: Register
        :param new: The new register to add to the data
        :type new: Register
        """
        idx = self._index_of(after)
        self._items.insert(idx + 1, new)
        self._refresh_indices(idx + 1)
        self._rebuild_type_index()

    def remove(self, r: Register) -> None:
        """
        Removes an existing register in the chain.

        :param r: The register to be removed
        :type r: Register
        """
        idx = self._index_of(r)
        del self._items[idx]
        r._container = None
        r._index = 0
        self._refresh_indices(idx)
        self._rebuild_type_index()

    def of_type(self, t: type[_T]) -> Generator[_T, None, None]:
        """
        A register generator that only returns registers of type T.

        :param t: The register type that is desired
        :type t: Type[_T]
        :yield: Registers filtered by type _T
        :rtype: Generator[_T, None, None]
        """
        indices: list[int] = []
        for cls, idx_list in self._type_index.items():
            if issubclass(cls, t):
                indices.extend(idx_list)
        indices.sort()
        for idx in indices:
            yield cast(_T, self._items[idx])

    def get_registers_of_type(
        self, t: type[_T], **kwargs: object
    ) -> _T | list[_T] | None:
        """
        A register or register list that only returns
        registers of type T that meet
        given filter requirements passed as kwargs.

        :param t: The register type that is desired
        :type t: Type[_T]
        :return: Registers filtered by type _T and optional properties
        :rtype: _T | list[_T] | None
        """

        def __meets(r: Any) -> bool:
            return all(
                getattr(r, k) == v for k, v in kwargs.items() if v is not None
            )

        filtered_registers = [r for r in self.of_type(t) if __meets(r)]
        if len(filtered_registers) == 0:
            return None
        elif len(filtered_registers) == 1:
            return filtered_registers[0]
        else:
            return filtered_registers

    def remove_registers_of_type(self, t: type[_T], **kwargs: object) -> None:
        """
        Removes a set of registers given a type and an optional group of
        filters, similar to `get_registers_of_type()`

        :param t: The register type that is desired
        :type t: Type[_T]
        """
        filtered_registers = self.get_registers_of_type(t, **kwargs)
        if isinstance(filtered_registers, t):
            self.remove(cast(Register, filtered_registers))
        elif isinstance(filtered_registers, list):
            for r in filtered_registers:
                if r is not self._items[0]:
                    self.remove(cast(Register, r))

    @property
    def first(self) -> Register:
        return self._items[0]

    @property
    def last(self) -> Register:
        return self._items[-1]
