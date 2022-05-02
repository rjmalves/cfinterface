from typing import List, Type

from cfinterface.components.section import Section
from cfinterface.components.defaultsection import DefaultSection
from cfinterface.data.sectiondata import SectionData
from cfinterface.reading.sectionreading import SectionReading
from cfinterface.writing.sectionwriting import SectionWriting


class SectionFile:
    """
    Class that models a file divided by registers, where the reading
    and writing are given by a series of registers.
    """

    SECTIONS: List[Type[Section]] = []

    def __init__(
        self,
        data=SectionData(DefaultSection("")),
    ) -> None:
        self.__data = data

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SectionFile):
            return False
        bf: SectionFile = o
        return self.data == bf.data

    @classmethod
    def read(cls, directory: str, filename: str = ""):
        """
        Reads the sectionfile data from a given file in disk.

        :param filename: The file name in disk
        :type filename: str
        :param directory: The directory where the file is
        :type directory: str
        """
        reader = SectionReading(cls.SECTIONS)
        return cls(reader.read(filename, directory))

    def write(self, directory: str, filename: str = ""):
        """
        Write the sectionfile data to a given file in disk.

        :param filename: The file name in disk
        :type filename: str
        :param directory: The directory where the file will be
        :type directory: str
        """
        writer = SectionWriting(self.__data)
        writer.write(filename, directory)

    @property
    def data(self) -> SectionData:
        return self.__data
