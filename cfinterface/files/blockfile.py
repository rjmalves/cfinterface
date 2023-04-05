from typing import List, Dict, Type, Optional, Union, IO

from cfinterface.components.block import Block
from cfinterface.components.defaultblock import DefaultBlock
from cfinterface.data.blockdata import BlockData
from cfinterface.reading.blockreading import BlockReading
from cfinterface.writing.blockwriting import BlockWriting


class BlockFile:
    """
    Class that models a file divided by blocks, where the reading
    and writing are given by a series of blocks.
    """

    VERSIONS: Dict[str, List[Type[Block]]] = {}
    BLOCKS: List[Type[Block]] = []
    ENCODING = "utf-8"
    STORAGE = "TEXT"
    __VERSION = "latest"

    def __init__(
        self,
        data=BlockData(DefaultBlock()),
    ) -> None:
        self.__data = data
        self.__storage = self.__class__.STORAGE
        self.__encoding = self.__class__.ENCODING

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BlockFile):
            return False
        bf: BlockFile = o
        return self.data == bf.data

    @classmethod
    def read(cls, content: Union[str, bytes], *args, **kwargs):
        """
        Reads the blockfile data from either a given file or a buffer.

        :param content: The file name in disk or the file contents themselves
        :type content: str | bytes
        """
        reader = BlockReading(cls.BLOCKS, cls.STORAGE)
        return cls(reader.read(content, cls.ENCODING, *args, **kwargs))

    def write(self, to: Union[str, IO], *args, **kwargs):
        """
        Write the blockfile data to a given file or buffer.

        :param to: The writing destination, being a string for writing
            to a file or the IO buffer
        :type to: str | IO
        """
        writer = BlockWriting(self.__data, self.__storage)
        writer.write(to, self.__encoding, *args, **kwargs)

    @property
    def data(self) -> BlockData:
        return self.__data

    @classmethod
    def set_version(cls, v: str):
        """
        Sets the file's version to be read. Different file versions
        may contain different blocks. The version to be set is considered
        is forced to the latest version with a new block set available.

        If a BlockFile has VERSIONS with keys {"v0": ..., "v1": ...},
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
            cls.BLOCKS = cls.VERSIONS.get(closest_version, cls.BLOCKS)
