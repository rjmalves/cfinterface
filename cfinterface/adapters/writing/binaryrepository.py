from typing import BinaryIO, Union

from cfinterface.adapters.writing.repository import Repository


class BinaryRepository(Repository):
    def __init__(self, path: str) -> None:
        super().__init__(path, None)
        self._filepointer: BinaryIO = None  # type: ignore

    def __enter__(self):
        self._filepointer = open(self._path, "wb")
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._filepointer.close()

    def write(self, data: Union[str, bytes]):
        """
        Writes an amount of information to a file.

        :param data: The bytes to be written
        :type data: str | bytes
        """
        if isinstance(data, bytes):
            self._filepointer.write(data)

    @property
    def file(self) -> BinaryIO:
        return self._filepointer
