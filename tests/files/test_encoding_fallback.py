"""The fallback encoding retry must not keep what the failed attempt read."""

from pathlib import Path

import pytest

from cfinterface.files.blockfile import BlockFile
from cfinterface.files.registerfile import RegisterFile
from cfinterface.files.sectionfile import SectionFile

NUM_LINES = 100


class _Blocks(BlockFile):
    BLOCKS = []
    ENCODING = ["utf-8", "latin-1", "ascii"]


class _Registers(RegisterFile):
    REGISTERS = []
    ENCODING = ["utf-8", "latin-1", "ascii"]


class _Sections(SectionFile):
    SECTIONS = []
    ENCODING = ["utf-8", "latin-1", "ascii"]


def _latin1_file(tmp_path: Path) -> Path:
    lines = [f"{f'LINE {i}':<500}\n" for i in range(NUM_LINES - 1)]
    lines.append("1º FCF / 2º SF\n")
    content = "".join(lines).encode("latin-1")
    # Past the text decoder's first chunk, so UTF-8 fails mid-file.
    assert content.index("º".encode("latin-1")) > 8192
    path = tmp_path / "file.dat"
    path.write_bytes(content)
    return path


@pytest.mark.parametrize("file_type", [_Blocks, _Registers, _Sections])
def test_latin1_file_is_read_once(tmp_path: Path, file_type: type) -> None:
    path = _latin1_file(tmp_path)

    data = file_type.read(str(path)).data

    lines = [str(component.data) for component in data][1:]
    assert len(lines) == NUM_LINES
    assert lines[0].startswith("LINE 0")
    assert lines[-1].startswith("1º FCF")
