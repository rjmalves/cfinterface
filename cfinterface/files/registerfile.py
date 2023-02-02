from typing import List, Type
import pandas as pd  # type: ignore
from cfinterface.components.register import Register
from cfinterface.components.defaultregister import DefaultRegister
from cfinterface.data.registerdata import RegisterData
from cfinterface.reading.registerreading import RegisterReading
from cfinterface.writing.registerwriting import RegisterWriting


class RegisterFile:
    """
    Class that models a file divided by registers, where the reading
    and writing are given by a series of registers.
    """

    REGISTERS: List[Type[Register]] = []
    ENCODING = "utf-8"
    STORAGE = "TEXT"

    def __init__(
        self,
        data=RegisterData(DefaultRegister(data="")),
    ) -> None:
        self.__data = data
        self.__storage = self.__class__.STORAGE
        self.__encoding = self.__class__.ENCODING

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
    def read(cls, directory: str, filename: str = ""):
        """
        Reads the registerfile data from a given file in disk.

        :param filename: The file name in disk
        :type filename: str
        :param directory: The directory where the file is
        :type directory: str
        """
        reader = RegisterReading(cls.REGISTERS, cls.STORAGE)
        return cls(reader.read(filename, directory, cls.ENCODING))

    def write(self, directory: str, filename: str = ""):
        """
        Write the registerfile data to a given file in disk.

        :param filename: The file name in disk
        :type filename: str
        :param directory: The directory where the file will be
        :type directory: str
        """
        writer = RegisterWriting(self.__data, self.__storage)
        writer.write(filename, directory, self.__encoding)

    @property
    def data(self) -> RegisterData:
        return self.__data
