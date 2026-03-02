# ticket-008 Migrate Internal Storage Parameter Usage to StorageType

## Context

### Background

After ticket-007 updated the factory functions to accept `StorageType`, the internal usage sites that pass `storage: str` parameters need to be migrated to use `StorageType` enum members. This includes class attributes (`STORAGE`), method parameters, and local variables throughout the component, reading, writing, and file layers.

### Relation to Epic

This is the fourth ticket in Epic 02 and the largest. It systematically converts all internal `storage: str` usage to `StorageType` while preserving backward compatibility for consumer code that sets `STORAGE = "TEXT"` as a class attribute.

### Current State

The `storage` parameter flows through the following path:

1. **Class attributes** (set by consumer subclasses):
   - `Section.STORAGE: str = "TEXT"` (`cfinterface/components/section.py` line 12)
   - `RegisterFile.STORAGE = "TEXT"` (`cfinterface/files/registerfile.py` line 23)
   - `BlockFile.STORAGE = "TEXT"` (`cfinterface/files/blockfile.py` line 21)
   - `SectionFile.STORAGE = "TEXT"` (`cfinterface/files/sectionfile.py` line 21)

2. **Method parameters** accepting `storage: str`:
   - `Register.matches(cls, line, storage: str = "")` (line 55)
   - `Register.read(self, file, storage: str = "", ...)` (line 67)
   - `Register.write(self, file, storage: str = "", ...)` (line 87)
   - `Register.read_register(self, file, storage: str = "", ...)` (line 107)
   - `Register.write_register(self, file, storage: str = "", ...)` (line 116)
   - `Block.begins(cls, line, storage: str = "")` (line 32)
   - `Block.ends(cls, line, storage: str = "")` (line 43)
   - `DefaultRegister.read(self, file, storage: str = "", ...)` (line 21)
   - `DefaultRegister.write(self, file, storage: str = "", ...)` (line 37)
   - `Line.__init__(self, ..., storage: str = "")` (line 30)

3. **Reading/Writing constructors**:
   - `RegisterReading.__init__(self, ..., storage: str = "")` (line 28)
   - `BlockReading.__init__(self, ..., storage: str = "")` (line 28)
   - `SectionReading.__init__(self, ..., storage: str = "")` (line 28)
   - `RegisterWriting.__init__(self, data, storage: str = "")` (line 21)
   - `BlockWriting.__init__(self, data, storage: str = "")` (line 20)
   - `SectionWriting.__init__(self, data, storage: str = "")` (line 21)

4. **String comparison in DefaultRegister**:
   - Line 31: `if storage not in ["BINARY"]:`
   - Line 47: `if storage not in ["BINARY"]:`

## Specification

### Requirements

1. Change all `STORAGE` class attributes from `str` type to `StorageType` type, using `StorageType.TEXT` as the default value
2. Change all `storage: str` parameter type hints to `storage: Union[str, StorageType]` (preserving backward compat)
3. Change default parameter values from `storage: str = ""` to `storage: Union[str, StorageType] = ""` (the empty string default triggers the TextualRepository fallback, which is the existing behavior)
4. In `DefaultRegister`, change `if storage not in ["BINARY"]:` to use `StorageType.BINARY` comparison
5. Update `Line.__init__` storage parameter to accept `Union[str, StorageType]`
6. All factory() calls already accept `Union[str, StorageType]` from ticket-007, so no changes needed there

### Inputs/Props

N/A -- internal refactoring.

### Outputs/Behavior

No observable behavior change. Both string and enum values work everywhere.

### Error Handling

No change -- the factory fallback handles unknown values as before.

## Acceptance Criteria

- [ ] Given `Section.STORAGE`, when inspected, then its default value is `StorageType.TEXT`
- [ ] Given `RegisterFile.STORAGE`, when inspected, then its default value is `StorageType.TEXT`
- [ ] Given `BlockFile.STORAGE`, when inspected, then its default value is `StorageType.TEXT`
- [ ] Given `SectionFile.STORAGE`, when inspected, then its default value is `StorageType.TEXT`
- [ ] Given `Register.matches()`, when called with `storage=StorageType.TEXT`, then it works correctly
- [ ] Given `Register.read()`, when called with `storage=StorageType.BINARY`, then it works correctly
- [ ] Given `DefaultRegister.read()` with `storage=StorageType.BINARY`, when called, then it sets `self.data = None` (binary path)
- [ ] Given `DefaultRegister.read()` with `storage=StorageType.TEXT`, when called, then it reads a line (text path)
- [ ] Given a consumer subclass that sets `STORAGE = "TEXT"` (string), when used, then it still works correctly (backward compat via str enum comparison)
- [ ] Given the full test suite, when `pytest tests/` is run, then all existing tests pass

## Implementation Guide

### Suggested Approach

Work through the files in dependency order:

**Step 1**: Update `cfinterface/components/section.py`:

```python
from cfinterface.storage import StorageType

class Section:
    STORAGE: Union[str, StorageType] = StorageType.TEXT
```

**Step 2**: Update `cfinterface/components/line.py`:

```python
from cfinterface.storage import StorageType

class Line:
    def __init__(
        self,
        fields: List[Field],
        values: Optional[List[Any]] = None,
        delimiter: Optional[Union[str, bytes]] = None,
        storage: Union[str, StorageType] = "",
    ):
```

**Step 3**: Update `cfinterface/components/register.py`:

```python
from cfinterface.storage import StorageType

class Register:
    @classmethod
    def matches(cls, line: Union[str, bytes], storage: Union[str, StorageType] = ""):
        ...
    def read(self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs) -> bool:
        ...
    def write(self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs) -> bool:
        ...
```

**Step 4**: Update `cfinterface/components/block.py`:

```python
from cfinterface.storage import StorageType

class Block:
    @classmethod
    def begins(cls, line: Union[str, bytes], storage: Union[str, StorageType] = ""):
        ...
    @classmethod
    def ends(cls, line: Union[str, bytes], storage: Union[str, StorageType] = ""):
        ...
```

**Step 5**: Update `cfinterface/components/defaultregister.py`:

```python
from cfinterface.storage import StorageType

class DefaultRegister(Register):
    def read(self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs) -> bool:
        if storage != StorageType.BINARY:
            self.data = file.readline()
        else:
            self.data = None
        return True

    def write(self, file: IO, storage: Union[str, StorageType] = "", *args, **kwargs) -> bool:
        if storage != StorageType.BINARY:
            file.write(self.data)
        return True
```

Note: The comparison `storage != StorageType.BINARY` works with both strings and enum because `StorageType.BINARY == "BINARY"`. The old `storage not in ["BINARY"]` is equivalent.

**Step 6**: Update the 3 reading classes and 3 writing classes with `Union[str, StorageType]` type hints on their `storage` parameters.

**Step 7**: Update the 3 file classes (`RegisterFile`, `BlockFile`, `SectionFile`) `STORAGE` attribute to `StorageType.TEXT`.

### Key Files to Modify

- `cfinterface/components/section.py`
- `cfinterface/components/line.py`
- `cfinterface/components/register.py`
- `cfinterface/components/block.py`
- `cfinterface/components/defaultregister.py`
- `cfinterface/reading/registerreading.py`
- `cfinterface/reading/blockreading.py`
- `cfinterface/reading/sectionreading.py`
- `cfinterface/writing/registerwriting.py`
- `cfinterface/writing/blockwriting.py`
- `cfinterface/writing/sectionwriting.py`
- `cfinterface/files/registerfile.py`
- `cfinterface/files/blockfile.py`
- `cfinterface/files/sectionfile.py`

### Patterns to Follow

- Always use `Union[str, StorageType]` for parameters (not just `StorageType`) to preserve backward compat
- Use `StorageType.TEXT` for default class attribute values
- Keep empty string `""` as the default for method parameters (it triggers the TextualRepository fallback)

### Pitfalls to Avoid

- Do NOT change the default parameter value from `""` to `StorageType.TEXT` in method signatures -- the empty string default is intentional and used by code that does not specify a storage type
- Do NOT break circular imports -- `cfinterface/storage.py` has no imports from cfinterface submodules, so importing it is safe everywhere
- The `storage not in ["BINARY"]` comparison in `DefaultRegister` uses list containment, not equality. Replace it with `storage != StorageType.BINARY` which is equivalent for both `"BINARY"` and `StorageType.BINARY` inputs
- Consumer subclasses that set `STORAGE = "TEXT"` (plain string) must still work -- since `StorageType(str, Enum)` compares equal to strings, this is safe

## Testing Requirements

### Unit Tests

Add tests that verify enum values work in the component layer:

```python
from cfinterface.storage import StorageType
from cfinterface.components.register import Register
from cfinterface.components.block import Block


def test_register_matches_with_enum():
    """Verify Register.matches works with StorageType."""
    class TestReg(Register):
        IDENTIFIER = "TEST"
        IDENTIFIER_DIGITS = 4

    assert TestReg.matches("TEST data", StorageType.TEXT)
    assert not TestReg.matches("OTHER data", StorageType.TEXT)


def test_block_begins_with_enum():
    """Verify Block.begins works with StorageType."""
    class TestBlock(Block):
        BEGIN_PATTERN = "BEGIN"

    assert TestBlock.begins("BEGIN of block", StorageType.TEXT)
```

### Integration Tests

Run `pytest tests/` to verify all 25 existing test files pass.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-007
- **Blocks**: ticket-009

## Effort Estimate

**Points**: 3
**Confidence**: High
