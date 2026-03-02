"""
RegisterFile Round-Trip
========================

This example demonstrates the core read/write round-trip workflow using
``Register``, ``Line``, ``Field``, and ``RegisterFile``.

We define two register types with different line patterns, build a
temporary file, read it back with the framework, inspect the parsed
data, and verify that writing produces identical output.
"""

# %%
# Define the register types
# --------------------------
# Each ``Register`` subclass declares an ``IDENTIFIER`` (the beginning
# pattern of the line) and a ``LINE`` composed of ``Field`` instances.

from datetime import datetime

from cfinterface.components import (
    DatetimeField,
    FloatField,
    Line,
    LiteralField,
    Register,
)
from cfinterface.files import RegisterFile


class DataHigh(Register):
    IDENTIFIER = "DATA_HIGH"
    IDENTIFIER_DIGITS = 9
    LINE = Line(
        [
            LiteralField(size=8, starting_position=11),
            LiteralField(size=11, starting_position=19),
            DatetimeField(size=12, starting_position=30, format="%m/%d/%Y"),
            FloatField(size=8, starting_position=42, decimal_digits=2),
        ]
    )

    @property
    def field_id(self) -> str:
        return self.data[0]

    @property
    def user(self) -> str:
        return self.data[1]

    @property
    def date(self) -> datetime:
        return self.data[2]

    @property
    def value(self) -> float:
        return self.data[3]


class DataLow(Register):
    IDENTIFIER = "DATA_LOW"
    IDENTIFIER_DIGITS = 8
    LINE = Line(
        [
            DatetimeField(size=12, starting_position=11, format="%m/%d/%Y"),
            FloatField(size=10, starting_position=23, decimal_digits=2),
        ]
    )

    @property
    def date(self) -> datetime:
        return self.data[0]

    @property
    def value(self) -> float:
        return self.data[1]


# %%
# Define the file model
# ----------------------
# The ``RegisterFile`` lists the register types it expects.


class MyRegisterFile(RegisterFile):
    REGISTERS = [DataHigh, DataLow]

    @property
    def data_high(self) -> list[DataHigh] | None:
        return self.data.get_registers_of_type(DataHigh)

    @property
    def data_low(self) -> list[DataLow] | None:
        return self.data.get_registers_of_type(DataLow)


# %%
# Write a sample file and read it back
# --------------------------------------
# We create a temporary file with known content, then let the framework
# parse it and verify the extracted values.

import tempfile
from pathlib import Path

# Field positions (0-indexed in the full line):
#   DataHigh: ID@11(8) User@19(11) Date@30(12) Value@42(8)
#   DataLow:  Date@11(12) Value@23(10)
SAMPLE_CONTENT = (
    "DATA_HIGH  ID001   sudo.user  10/20/2025  901.25\n"
    "DATA_HIGH  ID002   sudo.user  10/21/2025  100.20\n"
    "DATA_HIGH  ID003   test.user  10/30/2025  100.20\n"
    "\n"
    "DATA_LOW   01/01/2024    105.23\n"
    "DATA_LOW   01/02/2024     29.15\n"
    "DATA_LOW   01/03/2024      5.05\n"
)

with tempfile.TemporaryDirectory() as tmpdir:
    path = Path(tmpdir) / "registers.txt"
    path.write_text(SAMPLE_CONTENT)

    file = MyRegisterFile.read(str(path))

    # Inspect parsed registers
    print(f"DataHigh count: {len(file.data_high)}")
    for reg in file.data_high:
        print(f"  {reg.field_id}  {reg.user}  {reg.date}  {reg.value}")

    print(f"\nDataLow count: {len(file.data_low)}")
    for reg in file.data_low:
        print(f"  {reg.date}  {reg.value}")

    # Write back and verify round-trip
    out_path = Path(tmpdir) / "registers_out.txt"
    file.write(str(out_path))
    print(f"\nRound-trip successful: {out_path.exists()}")
