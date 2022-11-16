from typing import List, Type, Union
from os.path import join

from cfinterface.components.register import Register
from cfinterface.components.defaultregister import DefaultRegister
from cfinterface.data.registerdata import RegisterData

from cfinterface.adapters.reading.repository import Repository, factory


class RegisterReading:
    """
    Class for reading custom files based on a RegisterData structure.
    """

    def __init__(
        self,
        allowed_registers: List[Type[Register]],
        storage: str = "",
        linesize: int = 1,
    ) -> None:
        self.__allowed_registers = allowed_registers
        self.__data = RegisterData(DefaultRegister(data=""))
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

        :param file: The filepointer
        :type file: IO
        """
        self.__repository.file.seek(self.__last_position_filepointer)

    def __find_starting_register(
        self, registerdata: Union[str, bytes]
    ) -> Type[Register]:
        """
        Searches among the given registers for the register that begins in
        a line of the reading file.

        :param registerdata: A portion of data in the reading file
        :type registerdata: str | bytes
        :return: The register type that begins on the given line
        :rtype: Type[Register]
        """
        for r in self.__allowed_registers:
            if r.matches(registerdata, self.__storage):
                return r
        return DefaultRegister

    def __read_file(self) -> RegisterData:
        """
        Reads all the registers from the given registers in a file and
        returns the RegisterData structure.

        :return: The register data from the file
        :rtype: RegisterData
        """
        while True:
            line = self.__read_line_with_backup()
            if len(line) == 0:
                break
            self.__restore_previous_line()
            registertype = self.__find_starting_register(line)
            register = registertype()
            register.read(self.__repository.file, self.__storage)
            self.__data.append(register)
        return self.__data

    def read(
        self, filename: str, directory: str, encoding: str
    ) -> RegisterData:
        """
        Reads a file with a given name in a given directory and
        extracts the data from the specified registers.

        :param filename: The name of the file
        :type filename: str
        :param directory: The directory where the file is
        :type directory: str
        :param encoding: The encoding for reading the file
        :type encoding: str
        :return: The data from the registers found in the file
        :rtype: RegisterData
        """
        filepath = join(directory, filename)
        self.__repository = factory(self.__storage)(filepath, encoding)
        with self.__repository:
            return self.__read_file()

    @property
    def data(self) -> RegisterData:
        return self.__data

    @property
    def empty(self) -> bool:
        return len(self.__data) == 1
