from typing import TypeVar, Type, Generator, Optional, Union, List

from cfinterface.components.section import Section


class SectionData:
    """
    Class for a storing, managing and accessing data for a section file.
    """

    __slots__ = ["__root", "__head"]

    T = TypeVar("T")

    def __init__(self, root: Section) -> None:
        self.__root = root
        self.__head = root

    def __iter__(self):
        current = self.__root
        while current:
            yield current
            current = current.next

    def __len__(self) -> int:
        count = 0
        for _ in self:
            count += 1
        return count

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SectionData):
            return False
        sd: SectionData = o
        if len(self) != len(sd):
            return False
        for r1, r2 in zip(self, sd):
            if r1 != r2:
                return False
        return True

    def preppend(self, s: Section):
        """
        Appends a section to the beginning of the data.

        :param s: The new section to preppended to the data.
        :type s: Section
        """
        self.add_before(self.__root, s)

    def append(self, s: Section):
        """
        Appends a section to the end of the data.

        :param s: The new section to append to the data
        :type s: Section
        """
        self.add_after(self.__head, s)

    def add_before(self, before: Section, new: Section):
        """
        Adds a new section to the data before another
        specified section.

        :param before: The existing section which will be preppended
        :type before: Section
        :param new: The new section to add to the data
        :type new: Section
        """
        if before == self.__root:
            self.__root = new
        else:
            if before.previous:
                before.previous.next = new
        new.previous = before.previous
        before.previous = new
        new.next = before

    def add_after(self, after: Section, new: Section):
        """
        Adds a new section to the data after another
        specified section.

        :param after: The existing section which will be appended
        :type after: Section
        :param new: The new section to add to the data
        :type new: Section
        """
        if after == self.__head:
            self.__head = new
        else:
            if after.next:
                after.next.previous = new
        new.next = after.next
        after.next = new
        new.previous = after

    def remove(self, s: Section):
        """
        Removes an existing section in the chain.

        :param s: The section to be removed
        :type s: Section
        """
        if s.previous is not None:
            s.previous.next = s.next
        if s.next is not None:
            s.next.previous = s.previous

    def of_type(self, t: Type[T]) -> Generator[T, None, None]:
        """
        A section generator that only returns sections of type T.

        :param t: The section type that is desired
        :type t: Type[T]
        :yield: Sections filtered by type T
        :rtype: Generator[T, None, None]
        """
        for s in self:
            if isinstance(s, t):
                yield s

    def get_sections_of_type(
        self, t: Type[T], **kwargs
    ) -> Optional[Union[T, List[T]]]:
        """
        A section or section list that only returns
        sections of type T that meet
        given filter requirements passed as kwargs.

        :param t: The section type that is desired
        :type t: Type[T]
        :return: Sections filtered by type T and optional properties
        :rtype: T | list[T] | None
        """

        def __meets(r) -> bool:
            conditions: List[bool] = []
            for k, v in kwargs.items():
                if v is not None:
                    conditions.append(getattr(r, k) == v)
            return all(conditions)

        all_sections_of_type = [b for b in self.of_type(t)]
        filtered_sections = [r for r in all_sections_of_type if __meets(r)]
        if len(filtered_sections) == 0:
            return None
        elif len(filtered_sections) == 1:
            return filtered_sections[0]
        else:
            return filtered_sections

    def remove_sections_of_type(self, t: Type[T], **kwargs):
        """
        Removes a set of sections given a type and an optional group of
        filters, similar to `get_sections_of_type()`

        :param t: The section type that is desired
        :type t: Type[T]
        """
        filtered_sections = self.get_sections_of_type(t, **kwargs)
        if isinstance(filtered_sections, t) and isinstance(
            filtered_sections, Section
        ):
            self.remove(filtered_sections)
        elif isinstance(filtered_sections, list):
            for s in filtered_sections:
                if isinstance(s, Section) and s != self.__root:
                    self.remove(s)

    @property
    def first(self) -> Section:
        return self.__root

    @property
    def last(self) -> Section:
        return self.__head
