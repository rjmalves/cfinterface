from typing import BinaryIO

from cfinterface.adapters.reading.repository import Repository


class BinaryRepository(Repository):
    def __init__(self, path: str) -> None:
        super().__init__(path, None)
        self._filepointer: BinaryIO = None  # type: ignore

    def __enter__(self):
        self._filepointer = open(self._path, "rb")
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._filepointer.close()

    def read(self, n: int) -> bytes:
        """
        Reads a line for extracting information following
        the given fields.

        :param n: The number of bytes to be read
        :type n: int
        :return: The extracted data
        :rtype: bytes
        """
        return self._filepointer.read(n)

    @property
    def file(self) -> BinaryIO:
        return self._filepointer
