"""
Tabular Parsing
================

This example demonstrates the ``TabularParser`` class for schema-driven
tabular data parsing, supporting both fixed-width and delimiter-separated
layouts.
"""

# %%
# Fixed-Width Parsing
# --------------------
# Define a column schema using ``ColumnDef`` named tuples, then parse
# fixed-width text lines into a dict-of-lists.

from cfinterface.components import FloatField, IntegerField, LiteralField
from cfinterface.components.tabular import ColumnDef, TabularParser

fixed_columns = [
    ColumnDef(name="City", field=LiteralField(size=12, starting_position=0)),
    ColumnDef(
        name="Population",
        field=IntegerField(size=10, starting_position=12),
    ),
    ColumnDef(
        name="Area",
        field=FloatField(size=8, starting_position=22, decimal_digits=1),
    ),
]

parser = TabularParser(fixed_columns)

lines = [
    "Springfield  1200000    115.4\n",
    "Shelbyville   800000     98.2\n",
    "Capital City  500000     72.0\n",
]

data = parser.parse_lines(lines)
print("=== Fixed-Width Parsing ===")
for i, city in enumerate(data["City"]):
    print(f"  {city}: pop={data['Population'][i]}, area={data['Area'][i]}")

# %%
# Round-Trip with format_rows
# ----------------------------
# ``format_rows()`` converts the parsed dict-of-lists back into
# fixed-width text lines.

roundtrip_lines = parser.format_rows(data)
print("\n=== Round-Trip Output ===")
for line in roundtrip_lines:
    print(f"  |{line.rstrip()}|")

# %%
# Delimiter-Separated Parsing
# ----------------------------
# For CSV-style data, pass a ``delimiter`` to the parser.
# When using a delimiter, ``starting_position`` is ignored and only
# ``size`` (max token width) applies.

delimited_columns = [
    ColumnDef(name="Name", field=LiteralField(size=20, starting_position=0)),
    ColumnDef(
        name="Score",
        field=FloatField(size=10, starting_position=0, decimal_digits=2),
    ),
    ColumnDef(name="Grade", field=LiteralField(size=2, starting_position=0)),
]

csv_parser = TabularParser(delimited_columns, delimiter=",")

csv_lines = [
    "Alice,95.50,A\n",
    "Bob,87.25,B\n",
    "Charlie,72.00,C\n",
]

csv_data = csv_parser.parse_lines(csv_lines)
print("\n=== Delimiter-Separated Parsing ===")
for i, name in enumerate(csv_data["Name"]):
    print(
        f"  {name}: score={csv_data['Score'][i]}, grade={csv_data['Grade'][i]}"
    )

# %%
# Formatting delimited data back
# --------------------------------

csv_roundtrip = csv_parser.format_rows(csv_data)
print("\n=== Delimited Round-Trip ===")
for line in csv_roundtrip:
    print(f"  {line.rstrip()}")
