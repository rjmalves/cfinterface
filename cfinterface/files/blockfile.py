from typing import IO, Dict, List, Type, Union

from cfinterface.components.block import Block
from cfinterface.components.defaultblock import DefaultBlock
from cfinterface.data.blockdata import BlockData
from cfinterface.reading.blockreading import BlockReading
from cfinterface.storage import StorageType, _ensure_storage_type
from cfinterface.writing.blockwriting import BlockWriting


class BlockFile:
    """
    Class that models a file divided by blocks, where the reading
    and writing are given by a series of blocks.
    """

    __slots__ = ["__data", "__storage", "__encoding"]

    VERSIONS: Dict[str, List[Type[Block]]] = {}
    BLOCKS: List[Type[Block]] = []
    ENCODING: Union[str, List[str]] = ["utf-8", "latin-1", "ascii"]
    STORAGE: Union[str, StorageType] = StorageType.TEXT
    __VERSION = "latest"

    def __init__(
        self,
        data=BlockData(DefaultBlock()),
    ) -> None:
        self.__data = data
        self.__storage = _ensure_storage_type(self.__class__.STORAGE)
        self.__encoding = (
            self.__class__.ENCODING
            if type(self.__class__.ENCODING) is str
            else self.__class__.ENCODING[0]
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BlockFile):
            return False
        return self.data == o.data

    @classmethod
    def read(cls, content: Union[str, bytes], *args, **kwargs):
        """
        Reads the blockfile data from either a given file or a buffer.

        :param content: The file name in disk or the file contents themselves
        :type content: str | bytes
        """
        reader = BlockReading(cls.BLOCKS, cls.STORAGE)
        if type(cls.ENCODING) is str:
            return cls(reader.read(content, cls.ENCODING, *args, **kwargs))
        else:
            for encoding in cls.ENCODING:
                try:
                    return cls(reader.read(content, encoding, *args, **kwargs))
                except UnicodeDecodeError:
                    pass
        raise EncodingWarning(
            "Failed to decode content with all specified encodings."
        )

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
        """
        Exposes the :class:`BlockData` object, which gives access
        to the methods:

        - `preppend()`
        - `append()`
        - `add_before()`
        - `add_after()`
        - `get_blocks_of_type()`


        :return: The data internal object
        :rtype: :class:`BlockData`
        """
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
        available_versions = sorted(cls.VERSIONS.keys())
        recent_versions = [ver for ver in available_versions if v >= ver]
        if recent_versions:
            cls.__VERSION = v
            cls.BLOCKS = cls.VERSIONS.get(recent_versions[-1], cls.BLOCKS)
