from typing import IO, List, Type
from os.path import join

from cfinterface.components.register import Register
from cfinterface.components.defaultregister import DefaultRegister
from cfinterface.data.registerdata import RegisterData


class RegisterReading:
    """
    Class for reading custom files based on a RegisterData structure.
    """

    def __init__(self, allowed_registers: List[Type[Register]]) -> None:
        self.__allowed_registers = allowed_registers
        self.__data = RegisterData(DefaultRegister(data=""))
        self.__last_position_filepointer = 0

    def __read_line_with_backup(self, file: IO) -> str:
        """
        Reads a line of the file, saving the filepointer position
        in case one desired to return to the previous line.

        :param file: THe filepoiner for the reading file
        :type file: IO
        :return: The read line
        :rtype: str
        """
        self.__last_position_filepointer = file.tell()
        return file.readline()

    def __restore_previous_line(self, file: IO):
        """
        Restores the filepointer to the beginning of the previously
        read line.

        :param file: The filepointer
        :type file: IO
        """
        file.seek(self.__last_position_filepointer)

    def __find_starting_register(self, line: str) -> Type[Register]:
        """
        Searches among the given registers for the register that begins in
        a line of the reading file.

        :param line: A line of the reading file
        :type line: str
        :return: The register type that begins on the given line
        :rtype: Type[Register]
        """
        for r in self.__allowed_registers:
            if r.matches(line):
                return r
        return DefaultRegister

    def __read_file(self, file: IO) -> RegisterData:
        """
        Reads all the registers from the given registers in a file and
        returns the RegisterData structure.

        :param file: The filepointer
        :type file: IO
        :return: The register data from the file
        :rtype: RegisterData
        """
        while True:
            line = self.__read_line_with_backup(file)
            if len(line) == 0:
                break
            self.__restore_previous_line(file)
            registertype = self.__find_starting_register(line)
            register = registertype()
            register.read(file)
            self.__data.append(register)
        return self.__data

    def read(self, filename: str, directory: str) -> RegisterData:
        """
        Reads a file with a given name in a given directory and
        extracts the data from the specified registers.

        :param filename: The name of the file
        :type filename: str
        :param directory: The directory where the file is
        :type directory: str
        :return: The data from the registers found in the file
        :rtype: RegisterData
        """
        filepath = join(directory, filename)
        with open(filepath, "r") as fp:
            return self.__read_file(fp)

    @property
    def data(self) -> RegisterData:
        return self.__data

    @property
    def empty(self) -> bool:
        return len(self.__data) == 1
