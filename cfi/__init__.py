"""
cfi
====

cfi is a Python module for handling custom formatted files
and provide reading, storing and writing utilities.
"""

__version__ = "0.0.1"

from cfi.components.defaultblock import DefaultBlock
from cfi.data.blockdata import BlockData
from cfi.reading.blockreading import BlockReading
from cfi.writing.blockwriting import BlockWriting
from cfi.files.blockfile import BlockFile
