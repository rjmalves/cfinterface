from typing import List, Type, Union
from os.path import isfile

from cfinterface.components.section import Section
from cfinterface.components.defaultsection import DefaultSection
from cfinterface.data.sectiondata import SectionData

from cfinterface.adapters.reading.repository import Repository, factory


class SectionReading:
    """
    Class for reading custom files based on a SectionData structure.
    """

    __slots__ = [
        "__sections",
        "__data",
        "__last_position_filepointer",
        "__storage",
        "__linesize",
        "__repository",
    ]

    def __init__(
        self,
        sections: List[Type[Section]],
        storage: str = "",
        linesize: int = 1,
    ) -> None:
        self.__sections = sections
        self.__data = SectionData(DefaultSection(data=""))
        self.__last_position_filepointer = 0
        self.__storage = storage
        self.__repository: Repository = None  # type: ignore
        self.__linesize = linesize

    def __read_line_with_backup(self) -> Union[str, bytes]:
        """
        Reads a line of the file, saving the filepointer position
        in case one desired to return to the previous line.


        :return: The read line
        :rtype: str | bytes
        """
        self.__last_position_filepointer = self.__repository.file.tell()
        return self.__repository.read(self.__linesize)

    def __restore_previous_line(self):
        """
        Restores the filepointer to the beginning of the previously
        read line.

        """
        self.__repository.file.seek(self.__last_position_filepointer)

    def __read_file(self, *args, **kwargs) -> SectionData:
        """
        Reads all the sections from a file and
        returns the SectionData structure.

        :return: The section data from the file
        :rtype: SectionData
        """
        for sectiontype in self.__sections:
            section = sectiontype()
            section.read(self.__repository.file, *args, **kwargs)
            self.__data.append(section)
        while True:
            line = self.__read_line_with_backup()
            if len(line) == 0:
                break
            self.__restore_previous_line()
            section = DefaultSection()
            section.read(self.__repository.file, *args, **kwargs)
            self.__data.append(section)
        return self.__data

    def read(
        self, content: Union[str, bytes], encoding: str, *args, **kwargs
    ) -> SectionData:
        """
        Reads a file with a given name in a given directory and
        extracts the data from the specified sections.

        :param content: The file name in disk or the file contents
        :type content: str | bytes
        :param encoding: The encoding for reading the file
        :type encoding: str
        :return: The data from the sections found in the file
        :rtype: SectionData
        """
        self.__repository = factory(self.__storage)(
            content, not isfile(content), encoding
        )
        with self.__repository:
            return self.__read_file(*args, **kwargs)

    @property
    def data(self) -> SectionData:
        return self.__data

    @property
    def empty(self) -> bool:
        return len(self.__data) == 1
