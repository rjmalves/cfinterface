import warnings
from typing import IO, TYPE_CHECKING, Any

from cfinterface.components.block import Block
from cfinterface.components.defaultblock import DefaultBlock
from cfinterface.data.blockdata import BlockData
from cfinterface.reading.blockreading import BlockReading
from cfinterface.storage import StorageType, _ensure_storage_type
from cfinterface.versioning import resolve_version
from cfinterface.writing.blockwriting import BlockWriting

if TYPE_CHECKING:
    from cfinterface.versioning import VersionMatchResult


class BlockFile:
    """
    Class that models a file divided by blocks, where the reading
    and writing are given by a series of blocks.
    """

    __slots__ = ["__data", "__storage", "__encoding"]

    VERSIONS: dict[str, list[type[Block]]] = {}
    BLOCKS: list[type[Block]] = []
    ENCODING: str | list[str] = ["utf-8", "latin-1", "ascii"]
    STORAGE: str | StorageType = StorageType.TEXT
    __VERSION = "latest"

    def __init__(
        self,
        data: BlockData = BlockData(DefaultBlock()),  # noqa: B008
    ) -> None:
        self.__data: BlockData = data
        self.__storage: str | StorageType = _ensure_storage_type(
            self.__class__.STORAGE
        )
        self.__encoding: str = (
            self.__class__.ENCODING
            if type(self.__class__.ENCODING) is str
            else self.__class__.ENCODING[0]
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BlockFile):
            return False
        return self.data == o.data

    @classmethod
    def read(
        cls,
        content: str | bytes,
        *args: Any,
        version: str | None = None,
        **kwargs: Any,
    ) -> "BlockFile":
        """Read from a file path or buffer. ``version`` selects a component set
        from VERSIONS without mutating the class."""
        components = cls.BLOCKS
        if version is not None and cls.VERSIONS:
            resolved = resolve_version(version, cls.VERSIONS)
            if resolved is not None:
                components = resolved
            else:
                warnings.warn(
                    f"No matching version for '{version}' in "
                    f"{cls.__name__}.VERSIONS. Using default components.",
                    stacklevel=2,
                )
        reader = BlockReading(components, cls.STORAGE)
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

    def write(self, to: str | IO[Any], *args: Any, **kwargs: Any) -> None:
        writer = BlockWriting(self.__data, self.__storage)
        writer.write(to, self.__encoding, *args, **kwargs)

    @classmethod
    def read_many(
        cls,
        paths: list[str],
        *,
        version: str | None = None,
    ) -> dict[str, "BlockFile"]:
        """Read multiple files and return a dict keyed by file path.

        Parameters
        ----------
        paths : list[str]
            File paths to read.
        version : str or None, optional
            Version key passed to :meth:`read`. Defaults to None.

        Returns
        -------
        dict[str, BlockFile]
            Mapping from each file path to its parsed BlockFile instance.
        """
        return {path: cls.read(path, version=version) for path in paths}

    def validate(
        self,
        version: str | None = None,
        threshold: float = 0.5,
    ) -> "VersionMatchResult":
        """Validate parsed data against expected component types."""
        from cfinterface.versioning import resolve_version, validate_version

        expected = self.__class__.BLOCKS
        if version is not None and self.__class__.VERSIONS:
            resolved = resolve_version(version, self.__class__.VERSIONS)
            if resolved is None:
                result = validate_version(
                    self.data, expected, DefaultBlock, threshold
                )
                return result._replace(matched=False)
            expected = resolved
        return validate_version(self.data, expected, DefaultBlock, threshold)

    @property
    def data(self) -> BlockData:
        return self.__data

    @classmethod
    def set_version(cls, v: str) -> None:
        """
        Set the active block set for the given version key.

        Resolves to the latest available version <= v, so an out-of-range
        key falls back to the nearest known version.

        .. deprecated::
            Use ``read(content, version="...")`` instead.
        """
        warnings.warn(
            "set_version() is deprecated. "
            'Use read(content, version="...") instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        resolved = resolve_version(v, cls.VERSIONS)
        if resolved is not None:
            cls.__VERSION = v
            cls.BLOCKS = resolved
