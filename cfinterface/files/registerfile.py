from typing import List, Type

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

    def __init__(
        self,
        data=RegisterData(DefaultRegister("")),
    ) -> None:
        self.__data = data

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RegisterFile):
            return False
        bf: RegisterFile = o
        return self.data == bf.data

    @classmethod
    def read(cls, directory: str, filename: str = ""):
        """
        Reads the registerfile data from a given file in disk.

        :param filename: The file name in disk
        :type filename: str
        :param directory: The directory where the file is
        :type directory: str
        """
        reader = RegisterReading(cls.REGISTERS)
        return cls(reader.read(filename, directory))

    def write(self, directory: str, filename: str = ""):
        """
        Write the registerfile data to a given file in disk.

        :param filename: The file name in disk
        :type filename: str
        :param directory: The directory where the file will be
        :type directory: str
        """
        writer = RegisterWriting(self.__data)
        writer.write(filename, directory)

    @property
    def data(self) -> RegisterData:
        return self.__data
