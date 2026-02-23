# ticket-017 Design Typed Field Read/Write Protocol

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Design and implement a typed protocol or generic base class for Field read/write operations that separates textual (`str`) and binary (`bytes`) code paths at the type level, eliminating the runtime `isinstance(line, bytes)` branch in `Field.read()` and `Field.write()`.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/components/field.py`, `cfinterface/components/floatfield.py`, `cfinterface/components/integerfield.py`, `cfinterface/components/literalfield.py`, `cfinterface/components/datetimefield.py`
- **Key decisions needed**:
  - Generic base class (`Field[T]` where T is `str | bytes`) vs. separate `TextualField`/`BinaryField` abstract classes
  - Whether to keep the current polymorphic `read(line: Union[str, bytes])` as a convenience wrapper or remove it entirely
  - Whether `_binary_read` and `_textual_read` should become the primary public API or remain internal
- **Open questions**:
  - Do consumers call `field.read()` directly, or is it always called via `Line.read()` which already knows the storage type?
  - Would a generic `Field[str]` / `Field[bytes]` approach work with Python 3.10's type system?

## Dependencies

- **Blocked By**: ticket-008 (StorageType must be in place)
- **Blocks**: ticket-018, ticket-019

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
