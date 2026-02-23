import warnings
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Type, Union

from cfinterface.components.defaultregister import DefaultRegister
from cfinterface.components.register import Register
from cfinterface.data.registerdata import RegisterData
from cfinterface.reading.registerreading import RegisterReading
from cfinterface.storage import StorageType, _ensure_storage_type
from cfinterface.versioning import resolve_version
from cfinterface.writing.registerwriting import RegisterWriting

if TYPE_CHECKING:
    from cfinterface.versioning import VersionMatchResult


class RegisterFile:
    """
    Class that models a file divided by registers, where the reading
    and writing are given by a series of registers.
    """

    __slots__ = ["__data", "__storage", "__encoding"]

    VERSIONS: Dict[str, List[Type[Register]]] = {}
    REGISTERS: List[Type[Register]] = []
    ENCODING: Union[str, List[str]] = ["utf-8", "latin-1", "ascii"]
    STORAGE: Union[str, StorageType] = StorageType.TEXT
    __VERSION = "latest"

    def __init__(
        self,
        data=RegisterData(DefaultRegister(data="")),
    ) -> None:
        self.__data = data
        self.__storage = _ensure_storage_type(self.__class__.STORAGE)
        self.__encoding = (
            self.__class__.ENCODING
            if type(self.__class__.ENCODING) is str
            else self.__class__.ENCODING[0]
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RegisterFile):
            return False
        return self.data == o.data

    def _as_df(self, register_type: Type[Register]):
        """Return registers of the given type as a read-only DataFrame."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for _as_df(). "
                "Install it with: pip install cfinterface[pandas]"
            )
        registers = list(self.data.of_type(register_type))
        if len(registers) == 0:
            return pd.DataFrame()
        cols = registers[0].custom_properties
        return pd.DataFrame(
            data={c: [getattr(r, c) for r in registers] for c in cols}
        )

    @classmethod
    def read(
        cls,
        content: Union[str, bytes],
        *args,
        version: Optional[str] = None,
        **kwargs,
    ):
        """Read from a file path or buffer. ``version`` selects a component set
        from VERSIONS without mutating the class."""
        components = cls.REGISTERS
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
        reader = RegisterReading(components, cls.STORAGE, *args, **kwargs)
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
        writer = RegisterWriting(self.__data, self.__storage)
        writer.write(to, self.__encoding, *args, **kwargs)

    @classmethod
    def read_many(
        cls,
        paths: List[str],
        *,
        version: Optional[str] = None,
    ) -> Dict[str, "RegisterFile"]:
        return {path: cls.read(path, version=version) for path in paths}

    def validate(
        self,
        version: Optional[str] = None,
        threshold: float = 0.5,
    ) -> "VersionMatchResult":
        """Validate parsed data against expected component types."""
        from cfinterface.versioning import resolve_version, validate_version

        expected = self.__class__.REGISTERS
        if version is not None and self.__class__.VERSIONS:
            resolved = resolve_version(version, self.__class__.VERSIONS)
            if resolved is None:
                result = validate_version(
                    self.data, expected, DefaultRegister, threshold
                )
                return result._replace(matched=False)
            expected = resolved
        return validate_version(self.data, expected, DefaultRegister, threshold)

    @property
    def data(self) -> RegisterData:
        return self.__data

    @classmethod
    def set_version(cls, v: str):
        """
        Set the active register set for the given version key.

        Resolves to the latest available version <= v, so an out-of-range
        key falls back to the nearest known version.

        .. deprecated::
            Use ``read(content, version="...")`` instead.
        """
        warnings.warn(
            'set_version() is deprecated. Use read(content, version="...") instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        resolved = resolve_version(v, cls.VERSIONS)
        if resolved is not None:
            cls.__VERSION = v
            cls.REGISTERS = resolved
