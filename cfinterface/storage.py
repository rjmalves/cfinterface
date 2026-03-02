import warnings
from enum import Enum
from typing import Union


class StorageType(str, Enum):
    """
    Enum for the storage type of a file, determining whether
    the file is read/written in text or binary mode.

    Using ``str`` as a mixin ensures backward compatibility:
    ``StorageType.TEXT == "TEXT"`` evaluates to ``True``.
    """

    TEXT = "TEXT"
    BINARY = "BINARY"


def _ensure_storage_type(
    value: Union[str, "StorageType"],
) -> Union[str, "StorageType"]:
    """Validate and optionally convert a storage value.

    Emits a DeprecationWarning when a plain string is used
    instead of a StorageType enum member.
    """
    if isinstance(value, StorageType):
        return value
    if value == "":
        return value
    if value in ("TEXT", "BINARY"):
        warnings.warn(
            f'Using string "{value}" for storage type is deprecated. '
            f"Use StorageType.{value} instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return StorageType(value)
    return value
