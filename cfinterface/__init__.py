"""
cfi
====

cfi is a Python module for handling custom formatted files
and provide reading, storing and writing utilities.
"""

__version__ = "1.9.1"

from . import components  # noqa
from . import data  # noqa
from . import reading  # noqa
from . import writing  # noqa
from . import files  # noqa
from .storage import StorageType  # noqa
from .versioning import SchemaVersion as SchemaVersion  # noqa
from .versioning import VersionMatchResult as VersionMatchResult  # noqa
from .versioning import resolve_version as resolve_version  # noqa
from .versioning import validate_version as validate_version  # noqa
