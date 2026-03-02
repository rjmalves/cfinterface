# cfinterface

[![tests](https://github.com/rjmalves/cfinterface/workflows/tests/badge.svg)](https://github.com/rjmalves/cfinterface/actions)
[![codecov](https://codecov.io/gh/rjmalves/cfinterface/branch/main/graph/badge.svg?token=86ZXJGB854)](https://codecov.io/gh/rjmalves/cfinterface)
[![PyPI version](https://img.shields.io/pypi/v/cfinterface.svg)](https://pypi.org/project/cfinterface/)
[![Python versions](https://img.shields.io/pypi/pyversions/cfinterface.svg)](https://pypi.org/project/cfinterface/)

Python framework for modeling custom file formats with declarative reading, formatting, and writing.

## Key Features

- **Fields** — typed value containers (`LiteralField`, `IntegerField`, `FloatField`, `DatetimeField`) with positional formatting for both text and binary files
- **Line** — ordered collection of fields that models a single line or record
- **Register / RegisterFile** — single-line blocks identified by a beginning pattern, ideal for files with many line types
- **Block / BlockFile** — multi-line blocks with beginning/ending patterns, for complex structured files
- **Section / SectionFile** — ordered, non-overlapping divisions of file content
- **TabularParser** — schema-driven tabular parsing with fixed-width or delimiter-separated layouts
- **Versioning** — `VERSIONS` dict with `resolve_version()` and `validate_version()` for files that evolve over time
- **Binary support** — `StorageType.TEXT` / `StorageType.BINARY` for seamless text or binary I/O
- **Batch reading** — `read_many()` for reading multiple files in one call

## Install

`cfinterface` requires Python >= 3.10:

```
pip install cfinterface
```

### Optional Dependencies

For pandas DataFrame integration (`TabularParser.to_dataframe()`):

```
pip install cfinterface[pandas]
```

## Quick Start

Model a line-based file with `Register` and `RegisterFile`:

```python
from datetime import datetime
from cfinterface import (
    DatetimeField, FloatField, LiteralField, Line, Register, RegisterFile,
)

class DataHigh(Register):
    IDENTIFIER = "DATA_HIGH"
    IDENTIFIER_DIGITS = 9
    LINE = Line(
        [
            LiteralField(size=6, starting_position=11),
            LiteralField(size=9, starting_position=19),
            DatetimeField(size=10, starting_position=30, format="%m/%d/%Y"),
            FloatField(size=6, starting_position=42, decimal_digits=2),
        ]
    )

class MyFile(RegisterFile):
    REGISTERS = [DataHigh]

file = MyFile.read("data.txt")
for reg in file.data.get_registers_of_type(DataHigh):
    print(reg.data)
```

Parse tabular data with `TabularParser`:

```python
from cfinterface import IntegerField, FloatField, LiteralField
from cfinterface.components.tabular import ColumnDef, TabularParser

columns = [
    ColumnDef(name="City", field=LiteralField(size=12, starting_position=0)),
    ColumnDef(name="Pop", field=IntegerField(size=10, starting_position=12)),
    ColumnDef(name="Area", field=FloatField(size=8, starting_position=22, decimal_digits=1)),
]

parser = TabularParser(columns)
data = parser.parse_lines(["Springfield  1200000    115.4\n"])
# {"City": ["Springfield"], "Pop": [1200000], "Area": [115.4]}
```

## Documentation

Guides, tutorials, and API reference: https://rjmalves.github.io/cfinterface

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.
