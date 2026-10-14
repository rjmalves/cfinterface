from pathlib import Path

import pytest
from mypy import api

SUBCLASS_READS = """
from cfinterface.files.blockfile import BlockFile
from cfinterface.files.registerfile import RegisterFile
from cfinterface.files.sectionfile import SectionFile


class MySectionFile(SectionFile):
    pass


class MyRegisterFile(RegisterFile):
    pass


class MyBlockFile(BlockFile):
    pass


section: MySectionFile = MySectionFile.read("file.txt")
register: MyRegisterFile = MyRegisterFile.read("file.txt")
block: MyBlockFile = MyBlockFile.read("file.txt")
sections: dict[str, MySectionFile] = MySectionFile.read_many(["file.txt"])
registers: dict[str, MyRegisterFile] = MyRegisterFile.read_many(["file.txt"])
blocks: dict[str, MyBlockFile] = MyBlockFile.read_many(["file.txt"])
"""


@pytest.mark.slow
def test_read_is_typed_as_returning_the_subclass(tmp_path: Path):
    stdout, stderr, status = api.run(
        ["--cache-dir", str(tmp_path), "-c", SUBCLASS_READS]
    )
    assert status == 0, stdout + stderr
