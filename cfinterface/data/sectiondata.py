from collections.abc import Generator, Iterator
from typing import (
    Any,
    TypeVar,
    cast,
)

from cfinterface.components.section import Section

_T = TypeVar("_T")


class SectionData:
    """
    Class for a storing, managing and accessing data for a section file.
    """

    __slots__ = ["_items", "_type_index"]

    def __init__(self, root: Section) -> None:
        self._items: list[Section] = [root]
        self._type_index: dict[type[Section], list[int]] = {type(root): [0]}
        self._refresh_indices(0)

    def __iter__(self) -> Iterator[Section]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, idx: int) -> Section:
        return self._items[idx]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SectionData):
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

    def _index_of(self, item: Section) -> int:
        for i, s in enumerate(self._items):
            if s is item:
                return i
        raise ValueError("Section not found in container")

    def _rebuild_type_index(self) -> None:
        self._type_index = {}
        for i, item in enumerate(self._items):
            t = type(item)
            if t not in self._type_index:
                self._type_index[t] = []
            self._type_index[t].append(i)

    def preppend(self, s: Section) -> None:
        """
        Appends a section to the beginning of the data.

        :param s: The new section to preppended to the data.
        :type s: Section
        """
        self._items.insert(0, s)
        self._refresh_indices(0)
        self._rebuild_type_index()

    def append(self, s: Section) -> None:
        """
        Appends a section to the end of the data.

        :param s: The new section to append to the data
        :type s: Section
        """
        self._items.append(s)
        self._refresh_indices(len(self._items) - 1)
        t = type(s)
        if t not in self._type_index:
            self._type_index[t] = []
        self._type_index[t].append(len(self._items) - 1)

    def add_before(self, before: Section, new: Section) -> None:
        """
        Adds a new section to the data before another
        specified section.

        :param before: The existing section which will be preppended
        :type before: Section
        :param new: The new section to add to the data
        :type new: Section
        """
        idx = self._index_of(before)
        self._items.insert(idx, new)
        self._refresh_indices(idx)
        self._rebuild_type_index()

    def add_after(self, after: Section, new: Section) -> None:
        """
        Adds a new section to the data after another
        specified section.

        :param after: The existing section which will be appended
        :type after: Section
        :param new: The new section to add to the data
        :type new: Section
        """
        idx = self._index_of(after)
        self._items.insert(idx + 1, new)
        self._refresh_indices(idx + 1)
        self._rebuild_type_index()

    def remove(self, s: Section) -> None:
        """
        Removes an existing section in the chain.

        :param s: The section to be removed
        :type s: Section
        """
        idx = self._index_of(s)
        del self._items[idx]
        s._container = None
        s._index = 0
        self._refresh_indices(idx)
        self._rebuild_type_index()

    def of_type(self, t: type[_T]) -> Generator[_T, None, None]:
        """
        A section generator that only returns sections of type T.

        :param t: The section type that is desired
        :type t: Type[_T]
        :yield: Sections filtered by type _T
        :rtype: Generator[_T, None, None]
        """
        indices: list[int] = []
        for cls, idx_list in self._type_index.items():
            if issubclass(cls, t):
                indices.extend(idx_list)
        indices.sort()
        for idx in indices:
            yield cast(_T, self._items[idx])

    def get_sections_of_type(
        self, t: type[_T], **kwargs: object
    ) -> _T | list[_T] | None:
        """
        A section or section list that only returns
        sections of type T that meet
        given filter requirements passed as kwargs.

        :param t: The section type that is desired
        :type t: Type[_T]
        :return: Sections filtered by type _T and optional properties
        :rtype: _T | list[_T] | None
        """

        def __meets(r: Any) -> bool:
            return all(
                getattr(r, k) == v for k, v in kwargs.items() if v is not None
            )

        filtered_sections = [r for r in self.of_type(t) if __meets(r)]
        if len(filtered_sections) == 0:
            return None
        elif len(filtered_sections) == 1:
            return filtered_sections[0]
        else:
            return filtered_sections

    def remove_sections_of_type(self, t: type[_T], **kwargs: object) -> None:
        """
        Removes a set of sections given a type and an optional group of
        filters, similar to `get_sections_of_type()`

        :param t: The section type that is desired
        :type t: Type[_T]
        """
        filtered_sections = self.get_sections_of_type(t, **kwargs)
        if isinstance(filtered_sections, t):
            self.remove(cast(Section, filtered_sections))
        elif isinstance(filtered_sections, list):
            for s in filtered_sections:
                if s is not self._items[0]:
                    self.remove(cast(Section, s))

    @property
    def first(self) -> Section:
        return self._items[0]

    @property
    def last(self) -> Section:
        return self._items[-1]
