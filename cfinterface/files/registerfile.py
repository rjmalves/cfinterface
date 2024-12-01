from typing import IO, Dict, List, Optional, Type, Union

import pandas as pd  # type: ignore

from cfinterface.components.defaultregister import DefaultRegister
from cfinterface.components.register import Register
from cfinterface.data.registerdata import RegisterData
from cfinterface.reading.registerreading import RegisterReading
from cfinterface.writing.registerwriting import RegisterWriting


class RegisterFile:
    """
    Class that models a file divided by registers, where the reading
    and writing are given by a series of registers.
    """

    __slots__ = ["__data", "__storage", "__encoding"]

    VERSIONS: Dict[str, List[Type[Register]]] = {}
    REGISTERS: List[Type[Register]] = []
    ENCODING: Union[str, List[str]] = ["utf-8", "latin-1", "ascii"]
    STORAGE = "TEXT"
    __VERSION = "latest"

    def __init__(
        self,
        data=RegisterData(DefaultRegister(data="")),
    ) -> None:
        self.__data = data
        self.__storage = self.__class__.STORAGE
        self.__encoding = (
            self.__class__.ENCODING
            if type(self.__class__.ENCODING) is str
            else self.__class__.ENCODING[0]
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RegisterFile):
            return False
        bf: RegisterFile = o
        return self.data == bf.data

    def _as_df(self, register_type: Type[Register]) -> pd.DataFrame:
        """
        Converts the registers of a given type to a dataframe for enabling
        read-only tasks. Changing the dataframe does not affect
        the file registers.

        :param register_type: The register_type to be converted
        :type register_type: Type[:class:`Register`]
        :return: The converted registers
        :rtype: pd.DataFrame
        """
        registers = [b for b in self.data.of_type(register_type)]
        if len(registers) == 0:
            return pd.DataFrame()
        cols = registers[0].custom_properties
        return pd.DataFrame(
            data={c: [getattr(r, c) for r in registers] for c in cols}
        )

    @classmethod
    def read(cls, content: Union[str, bytes], *args, **kwargs):
        """
        Reads the registerfile data from a given file in disk.

        :param content: The file name in disk or the file contents themselves
        :type content: str | bytes
        """
        reader = RegisterReading(cls.REGISTERS, cls.STORAGE, *args, **kwargs)
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
        Write the registerfile data to a given file or buffer.

        :param to: The writing destination, being a string for writing
            to a file or the IO buffer
        :type to: str | IO
        """
        writer = RegisterWriting(self.__data, self.__storage)
        writer.write(to, self.__encoding, *args, **kwargs)

    @property
    def data(self) -> RegisterData:
        """
        Exposes the :class:`RegisterData` object, which gives access
        to the methods:

        - `preppend()`
        - `append()`
        - `add_before()`
        - `add_after()`
        - `get_blocks_of_type()`


        :return: The data internal object
        :rtype: :class:`RegisterData`
        """
        return self.__data

    @classmethod
    def set_version(cls, v: str):
        """
        Sets the file's version to be read. Different file versions
        may contain different registers. The version to be set is considered
        is forced to the latest version with a new register set available.

        If a RegisterFile has VERSIONS with keys {"v0": ..., "v1": ...},
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
            cls.REGISTERS = cls.VERSIONS.get(closest_version, cls.REGISTERS)
