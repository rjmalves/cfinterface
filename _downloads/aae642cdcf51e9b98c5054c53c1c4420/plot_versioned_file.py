"""
Versioned BlockFile
====================

This example demonstrates file versioning in ``cfinterface``: defining
multiple versions of a block, reading with the ``version`` keyword, and
validating the parsed result against the expected schema.
"""

# %%
# Define versioned blocks
# ------------------------
# Two versions of a data block with different schemas.
# ``ConstantBlock`` exists in both versions; ``OldDataBlock`` is v1 only
# and ``NewDataBlock`` is v2 only.

import tempfile
from pathlib import Path
from typing import IO, Any

from cfinterface.components import (
    Block,
    FloatField,
    IntegerField,
    Line,
    LiteralField,
)
from cfinterface.files import BlockFile
from cfinterface.versioning import resolve_version


class ConstantBlock(Block):
    """A block that is present in every version of the file."""

    BEGIN_PATTERN = r"^FILE_HEADER"
    END_PATTERN = r"^END_FILE_HEADER"

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.readline()  # skip BEGIN_PATTERN line
        self.data = file.readline().strip()
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.write("FILE_HEADER\n")
        file.write(f"{self.data}\n")
        file.write("END_FILE_HEADER\n")
        return True


class OldDataBlock(Block):
    """Version 1.0 data block: integer ID and name only."""

    BEGIN_PATTERN = r"^DATA_BLOCK"
    END_PATTERN = r"^END_DATA"

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)
        self._line = Line(
            [
                IntegerField(size=5, starting_position=0),
                LiteralField(size=15, starting_position=5),
            ]
        )

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.readline()  # skip BEGIN_PATTERN
        rows = []
        while True:
            line = file.readline()
            if self.__class__.END_PATTERN.lstrip("^") in line or line == "":
                break
            rows.append(self._line.read(line))
        self.data = rows
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.write("DATA_BLOCK\n")
        for row in self.data:
            file.write(self._line.write(row))
        file.write("END_DATA\n")
        return True


class NewDataBlock(Block):
    """Version 2.0 data block: adds a float score column."""

    BEGIN_PATTERN = r"^DATA_BLOCK"
    END_PATTERN = r"^END_DATA"

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)
        self._line = Line(
            [
                IntegerField(size=5, starting_position=0),
                LiteralField(size=15, starting_position=5),
                FloatField(size=10, starting_position=20, decimal_digits=2),
            ]
        )

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.readline()  # skip BEGIN_PATTERN
        rows = []
        while True:
            line = file.readline()
            if self.__class__.END_PATTERN.lstrip("^") in line or line == "":
                break
            rows.append(self._line.read(line))
        self.data = rows
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.write("DATA_BLOCK\n")
        for row in self.data:
            file.write(self._line.write(row))
        file.write("END_DATA\n")
        return True


# %%
# Define the versioned file
# ---------------------------
# The ``VERSIONS`` dict maps version keys to component lists.
# ``BLOCKS`` provides the default (latest) schema.


class MyVersionedFile(BlockFile):
    VERSIONS = {
        "1.0": [ConstantBlock, OldDataBlock],
        "2.0": [ConstantBlock, NewDataBlock],
    }
    BLOCKS = [ConstantBlock, NewDataBlock]


# %%
# Read files with version selection
# ------------------------------------
# Use the ``version`` keyword to select which schema to apply.

V2_CONTENT = (
    "FILE_HEADER\n"
    "My Versioned File v2\n"
    "END_FILE_HEADER\n"
    "DATA_BLOCK\n"
    "    1 Alice             95.50\n"
    "    2 Bob               87.25\n"
    "END_DATA\n"
)

with tempfile.TemporaryDirectory() as tmpdir:
    v2_path = Path(tmpdir) / "v2.txt"
    v2_path.write_text(V2_CONTENT)

    file_v2 = MyVersionedFile.read(str(v2_path), version="2.0")

    print("=== Version 2.0 Read ===")
    for block in file_v2.data:
        print(f"  {type(block).__name__}: {block.data}")

    # %%
    # Validate version match
    # -----------------------
    # After reading, ``validate()`` checks if the parsed data matches
    # the expected schema for a given version.

    result = file_v2.validate(version="2.0")
    print("\n=== Version Validation ===")
    print(f"  Matched: {result.matched}")
    print(f"  Expected: {[t.__name__ for t in result.expected_types]}")
    print(f"  Found: {[t.__name__ for t in result.found_types]}")
    print(f"  Default ratio: {result.default_ratio:.1%}")

    # %%
    # resolve_version utility
    # ------------------------
    # Use ``resolve_version()`` to see which version key is selected
    # for a given request.

    components = resolve_version("1.5", MyVersionedFile.VERSIONS)
    resolved_names = [t.__name__ for t in components] if components else []
    print("\n=== resolve_version('1.5') ===")
    print(f"  Resolved to v1.0 components: {resolved_names}")
