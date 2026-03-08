"""
Reading files with BlockFile
=============================

This example demonstrates how to use ``Block`` and ``BlockFile`` to read and
write structured text files organized in blocks delimited by start and end
patterns.

We define two block types -- one for file metadata and another for data
records -- and perform the complete read-write cycle.
"""

# %%
# Defining the block types
# -------------------------
# Each ``Block`` subclass declares ``BEGIN_PATTERN`` (start pattern)
# and ``END_PATTERN`` (end pattern) as regular expressions. The
# ``read()`` and ``write()`` methods implement the reading and writing logic.

import tempfile
from io import StringIO
from pathlib import Path
from typing import IO, Any

from cfinterface.components import Block
from cfinterface.files import BlockFile


class HeaderBlock(Block):
    """Header block with general file information."""

    BEGIN_PATTERN = r"^CABECALHO"
    END_PATTERN = r"^FIM_CABECALHO"

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.readline()  # consume the BEGIN_PATTERN line
        fields: dict[str, str] = {}
        while True:
            line = file.readline()
            if not line or self.__class__.ends(line):
                break
            if "=" in line:
                key, _, value = line.partition("=")
                fields[key.strip()] = value.strip()
        self.data = fields
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.write("CABECALHO\n")
        for key, value in (self.data or {}).items():
            file.write(f"{key} = {value}\n")
        file.write("FIM_CABECALHO\n")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, HeaderBlock):
            return False
        return o.data == self.data


class DataBlock(Block):
    """Data block with records in key=value format per line."""

    BEGIN_PATTERN = r"^DADOS"
    END_PATTERN = r"^FIM_DADOS"

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.readline()  # consume the BEGIN_PATTERN line
        records: list[dict[str, str]] = []
        while True:
            line = file.readline()
            if not line or self.__class__.ends(line):
                break
            line = line.strip()
            if not line:
                continue
            fields = dict(
                pair.split("=", 1) for pair in line.split("|") if "=" in pair
            )
            fields = {k.strip(): v.strip() for k, v in fields.items()}
            if fields:
                records.append(fields)
        self.data = records
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.write("DADOS\n")
        for record in self.data or []:
            line = " | ".join(f"{k}={v}" for k, v in record.items())
            file.write(f"{line}\n")
        file.write("FIM_DADOS\n")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DataBlock):
            return False
        return o.data == self.data


# %%
# Defining the file model
# ------------------------
# The ``BlockFile`` subclass declares which block types the file can
# contain via ``BLOCKS``. Convenience properties expose the blocks
# by type using ``data.get_blocks_of_type()``.


class MyRecordFile(BlockFile):
    BLOCKS = [HeaderBlock, DataBlock]

    @property
    def header(self) -> HeaderBlock | None:
        return self.data.get_blocks_of_type(HeaderBlock)

    @property
    def records(self) -> list[DataBlock] | None:
        result = self.data.get_blocks_of_type(DataBlock)
        if result is None:
            return None
        if isinstance(result, list):
            return result
        return [result]


# %%
# Writing sample data and reading it back
# ----------------------------------------
# We create a temporary file with known content, let the framework
# perform the read, and verify the extracted values.

EXAMPLE_CONTENT = (
    "CABECALHO\n"
    "autor = joao.silva\n"
    "versao = 2.1\n"
    "data = 15/03/2025\n"
    "FIM_CABECALHO\n"
    "DADOS\n"
    "id=001 | nome=Produto A | preco=49.90\n"
    "id=002 | nome=Produto B | preco=129.00\n"
    "id=003 | nome=Produto C | preco=15.50\n"
    "FIM_DADOS\n"
    "DADOS\n"
    "id=101 | nome=Servico X | preco=299.00\n"
    "id=102 | nome=Servico Y | preco=199.00\n"
    "FIM_DADOS\n"
)

with tempfile.TemporaryDirectory() as tmpdir:
    path = Path(tmpdir) / "records.txt"
    path.write_text(EXAMPLE_CONTENT, encoding="utf-8")

    file_obj = MyRecordFile.read(str(path))

    # Inspect the header
    hdr = file_obj.header
    print("=== Header ===")
    for key, value in hdr.data.items():
        print(f"  {key}: {value}")

    # Inspect the data blocks
    print(f"\n=== Data Blocks ({len(file_obj.records)}) ===")
    for i, block in enumerate(file_obj.records, start=1):
        print(f"  Block {i} ({len(block.data)} records):")
        for rec in block.data:
            print(
                f"    id={rec['id']}  nome={rec['nome']}  preco={rec['preco']}"
            )

    # Write to a text buffer and verify the round-trip
    buffer = StringIO()
    file_obj.write(buffer)
    output_content = buffer.getvalue()

    input_lines = EXAMPLE_CONTENT.strip().splitlines()
    output_lines = output_content.strip().splitlines()
    print(
        f"\nRound-trip: {len(input_lines)} lines -> {len(output_lines)} lines"
    )

# %%
# Writing directly to a file
# ---------------------------
# ``BlockFile.write()`` accepts both a file path and an ``IO``
# object, making it easy to integrate with existing pipelines.

with tempfile.TemporaryDirectory() as tmpdir:
    input_path = Path(tmpdir) / "input.txt"
    output_path = Path(tmpdir) / "output.txt"

    input_path.write_text(EXAMPLE_CONTENT, encoding="utf-8")
    file_obj2 = MyRecordFile.read(str(input_path))
    file_obj2.write(str(output_path))

    print(f"\nOutput file created: {output_path.exists()}")
    print(f"Size: {output_path.stat().st_size} bytes")
