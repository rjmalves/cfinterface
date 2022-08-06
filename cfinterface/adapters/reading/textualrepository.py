from typing import TextIO

from cfinterface.adapters.reading.repository import Repository


class TextualRepository(Repository):
    def __init__(self, path: str, encoding: str) -> None:
        super().__init__(path, encoding)
        self._filepointer: TextIO = None  # type: ignore

    def __enter__(self):
        self._filepointer = open(self._path, "r", encoding=self._encoding)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._filepointer.close()

    def read(self, n: int) -> str:
        """
        Reads a line for extracting information following
        the given fields.

        :param n: The number of bytes to be read
        :type n: int
        :return: The extracted data
        :rtype: str
        """
        return self._filepointer.readline()

    @property
    def file(self) -> TextIO:
        return self._filepointer
