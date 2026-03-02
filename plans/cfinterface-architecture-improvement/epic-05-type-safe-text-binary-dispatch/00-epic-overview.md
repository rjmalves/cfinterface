# Epic 05: Type-Safe Text/Binary Dispatch

## Overview

After the `StorageType` enum is in place (Epic 02), this epic eliminates the pervasive `Union[str, bytes]` type threading throughout the adapter and component layers. Currently, methods like `Field.read(line: T)`, `Repository.matches(pattern, line)`, and `Line.read(line: Union[str, bytes])` accept both `str` and `bytes` and branch at runtime. This epic introduces protocol-based or generic typing to make the text/binary distinction a compile-time (type-checker) guarantee.

## Goals

1. Separate `TextualField` and `BinaryField` protocols/base classes
2. Remove runtime `isinstance(line, bytes)` checks from Field.read() and Field.write()
3. Make Repository classes fully typed (TextualRepository works with str, BinaryRepository with bytes)
4. Reduce `Union[str, bytes]` annotations to specific `str` or `bytes` where the storage type is known
5. Preserve backward compatibility for consumers that rely on the current polymorphic API

## Tickets

| Ticket     | Title                                                           | Effort |
| ---------- | --------------------------------------------------------------- | ------ |
| ticket-017 | Design typed Field read/write protocol                          | 2      |
| ticket-018 | Separate TextualRepository and BinaryRepository type signatures | 3      |
| ticket-019 | Update Line class for typed dispatch                            | 2      |
| ticket-020 | Update Register/Block/Section for typed IO paths                | 3      |

## Success Criteria

- mypy strict mode passes on the core modules
- Union[str, bytes] eliminated from hot code paths
- All existing tests pass
- No runtime performance regression
