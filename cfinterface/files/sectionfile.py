from typing import List, Dict, Type, Optional, Union, IO

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

    VERSIONS: Dict[str, List[Type[Section]]] = {}
    SECTIONS: List[Type[Section]] = []
    ENCODING = "utf-8"
    STORAGE = "TEXT"
    __VERSION = "latest"

    def __init__(
        self,
        data=SectionData(DefaultSection()),
    ) -> None:
        self.__data = data
        self.__storage = self.__class__.STORAGE
        self.__encoding = self.__class__.ENCODING

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SectionFile):
            return False
        bf: SectionFile = o
        return self.data == bf.data

    @classmethod
    def read(cls, content: Union[str, bytes], *args, **kwargs):
        """
        Reads the sectionfile data from a given file in disk.

        :param content: The file name in disk or the file contents themselves
        :type content: str | bytes
        """
        reader = SectionReading(cls.SECTIONS, cls.STORAGE)
        return cls(reader.read(content, cls.ENCODING, *args, **kwargs))

    def write(self, to: Union[str, IO], filename: str = "", *args, **kwargs):
        """
        Write the sectionfile data to a given file or buffer.

        :param to: The writing destination, being a string for writing
            to a file or the IO buffer
        :type to: str | IO
        """
        writer = SectionWriting(self.__data, self.__storage)
        writer.write(to, self.__encoding, *args, **kwargs)

    @property
    def data(self) -> SectionData:
        return self.__data

    @classmethod
    def set_version(cls, v: str):
        """
        Sets the file's version to be read. Different file versions
        may contain different sections. The version to be set is considered
        is forced to the latest version with a new section set available.

        If a SectionFile has VERSIONS with keys {"v0": ..., "v1": ...},
        calling `set_version("v2")` will set the version to `v1`.

        :param v: The file version to be read.
        :type v: str
        """

        def __find_closest_version() -> Optional[str]:
            available_versions = sorted(list(cls.VERSIONS.keys()))
            recent_versions = [
                version for version in available_versions if v >= version
            ]
            if len(recent_versions) > 0:
                return recent_versions[-1]
            return None

        closest_version = __find_closest_version()
        if closest_version is not None:
            cls.__VERSION = v
            cls.SECTIONS = cls.VERSIONS.get(closest_version, cls.SECTIONS)
