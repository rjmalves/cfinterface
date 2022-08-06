from typing import TextIO, Union

from cfinterface.adapters.writing.repository import Repository


class TextualRepository(Repository):
    def __init__(self, path: str, encoding: str) -> None:
        super().__init__(path, encoding)
        self._filepointer: TextIO = None  # type: ignore

    def __enter__(self):
        self._filepointer = open(self._path, "w", encoding=self._encoding)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._filepointer.close()

    def write(self, data: Union[str, bytes]):
        """
        Writes an amount of information to a file.

        :param data: The data to be written
        :type data: str | bytes
        """
        if isinstance(data, str):
            self._filepointer.write(data)

    @property
    def file(self) -> TextIO:
        return self._filepointer
