"""
Reading files with SectionFile
================================

This example demonstrates how to use ``Section`` and ``SectionFile`` to read
and write text files organized in sequential sections.

Unlike ``BlockFile`` (which searches for blocks by start pattern),
``SectionFile`` processes sections in a fixed order: each section reads what
it needs from the character stream and passes control to the next one.
"""

# %%
# Defining the sections
# ----------------------
# Each ``Section`` subclass implements ``read()`` and ``write()`` to
# process its part of the file. Reading is sequential -- the first
# section reads the beginning of the file, the second reads the
# continuation, and so on.

import tempfile
from io import StringIO
from pathlib import Path
from typing import IO, Any

from cfinterface.components import Section
from cfinterface.files import SectionFile


class HeaderSection(Section):
    """Header section: reads key=value pairs until a blank line."""

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        metadata: dict[str, str] = {}
        while True:
            line = file.readline()
            if not line or line.strip() == "":
                break
            if "=" in line:
                key, _, value = line.partition("=")
                metadata[key.strip()] = value.strip()
        self.data = metadata
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        for key, value in (self.data or {}).items():
            file.write(f"{key} = {value}\n")
        file.write("\n")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, HeaderSection):
            return False
        return o.data == self.data


class TableSection(Section):
    """Table section: reads data lines separated by '|' until EOF."""

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        records: list[list[str]] = []
        header: list[str] | None = None
        while True:
            line = file.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            columns = [c.strip() for c in line.split("|")]
            if header is None:
                header = columns
            else:
                records.append(columns)
        self.data = {"header": header or [], "records": records}
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        data = self.data or {"header": [], "records": []}
        header = data.get("header", [])
        records = data.get("records", [])
        if header:
            file.write(" | ".join(header) + "\n")
        for rec in records:
            file.write(" | ".join(rec) + "\n")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TableSection):
            return False
        return o.data == self.data


# %%
# Defining the file model
# ------------------------
# The ``SectionFile`` subclass declares the list of sections in ``SECTIONS``
# in the order they appear in the file. Convenience properties expose
# each section by type via ``data.get_sections_of_type()``.


class MyTabularFile(SectionFile):
    SECTIONS = [HeaderSection, TableSection]

    @property
    def header(self) -> HeaderSection | None:
        return self.data.get_sections_of_type(HeaderSection)

    @property
    def table(self) -> TableSection | None:
        return self.data.get_sections_of_type(TableSection)


# %%
# Writing sample data and reading it back
# ----------------------------------------
# We use a temporary file with known content to demonstrate the complete
# read cycle. The first section (header) consumes the key=value pairs
# followed by a blank line; the second section (table) consumes the
# remainder of the file.

EXAMPLE_CONTENT = (
    "titulo = Relatorio de Vendas\n"
    "responsavel = maria.souza\n"
    "periodo = 2025-Q1\n"
    "\n"
    "produto | quantidade | receita\n"
    "Widget A | 1200 | 59880.00\n"
    "Widget B | 850 | 127500.00\n"
    "Widget C | 430 | 21500.00\n"
    "Servico X | 60 | 18000.00\n"
)

with tempfile.TemporaryDirectory() as tmpdir:
    path = Path(tmpdir) / "report.txt"
    path.write_text(EXAMPLE_CONTENT, encoding="utf-8")

    file_obj = MyTabularFile.read(str(path))

    # Inspect the header
    hdr = file_obj.header
    print("=== Header ===")
    for key, value in hdr.data.items():
        print(f"  {key}: {value}")

    # Inspect the table
    tab = file_obj.table
    header_cols = tab.data["header"]
    records = tab.data["records"]

    print(f"\n=== Table ({len(records)} records) ===")
    print("  " + " | ".join(header_cols))
    print("  " + "-" * 50)
    for rec in records:
        print("  " + " | ".join(rec))

# %%
# Round-trip via in-memory buffer
# --------------------------------
# ``SectionFile.write()`` accepts an ``IO`` object in addition to a path.
# Here we write to a ``StringIO`` and confirm that the content was preserved.

with tempfile.TemporaryDirectory() as tmpdir:
    path = Path(tmpdir) / "report.txt"
    path.write_text(EXAMPLE_CONTENT, encoding="utf-8")

    file_obj2 = MyTabularFile.read(str(path))

    buffer = StringIO()
    file_obj2.write(buffer)
    output_content = buffer.getvalue()

    input_lines = EXAMPLE_CONTENT.strip().splitlines()
    output_lines = output_content.strip().splitlines()
    print(
        f"\nRound-trip: {len(input_lines)} input lines -> "
        f"{len(output_lines)} output lines"
    )

# %%
# Iterating over all sections
# ----------------------------
# ``SectionData`` is iterable: iterating over ``file_obj.data`` returns all
# sections in the order they were read, including the default
# ``DefaultSection`` that occupies index 0.

with tempfile.TemporaryDirectory() as tmpdir:
    path = Path(tmpdir) / "report.txt"
    path.write_text(EXAMPLE_CONTENT, encoding="utf-8")

    file_obj3 = MyTabularFile.read(str(path))

    print("\n=== All sections ===")
    for sec in file_obj3.data:
        print(f"  {type(sec).__name__}")
