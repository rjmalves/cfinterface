# ticket-026 Add Batch read_many() API to File Classes

## Context

### Background

Consumers like sintetizador-newave read 100+ files of the same type in a loop, each time calling `set_version()` and then `read()`. This is repetitive and error-prone -- the version must be set before every read, and if any intermediate code resets the version, subsequent reads silently produce wrong results.

With the `version` parameter introduced in ticket-025, the repetitive `set_version()` call is already eliminated per-file. This ticket adds a convenience `read_many()` classmethod that reads multiple files with shared settings (version, encoding override) in a single call, returning a dictionary keyed by file path.

The implementation is intentionally simple -- a sequential loop over `read()` calls. No parallelism, no complex infrastructure. The value is in the API convenience and the shared version context, not in performance optimization.

### Relation to Epic

This is the consumer-convenience ticket of epic-07. It builds on ticket-025's `version` parameter to offer a batch API that eliminates the per-file configuration loop. It is not blocking any other ticket and is independently valuable.

### Current State

The sintetizador-newave pattern for batch reads looks like:

```python
# Current consumer pattern (sintetizador-newave/app/adapters/repository/files.py):
def __read_nwlistop_setting_version(self, reader: Type[BlockFile], path: str):
    reader.set_version(self.__version)
    return reader.read(path).valores
```

This is called in lambdas across ~50 different file types, each time with a different path but the same version. A `read_many()` would reduce this to:

```python
files = MyBlockFile.read_many([path1, path2, ...], version=self.__version)
```

The `read()` classmethod on all three file classes accepts `content: Union[str, bytes]` as its first argument. When `content` is a string that is a valid file path (checked via `os.path.isfile`), it is read from disk. When it is a string that is not a file path, it is treated as raw content. `read_many()` will only accept file paths (strings), not raw content buffers.

## Specification

### Requirements

1. Add a `read_many()` classmethod to `RegisterFile`, `BlockFile`, and `SectionFile`
2. Signature: `read_many(cls, paths: List[str], *, version: Optional[str] = None) -> Dict[str, Self]` where `Self` is the file class type (use string annotation or `TypeVar` for the return type since `Self` requires Python 3.11)
3. `read_many()` iterates over `paths`, calls `cls.read(path, version=version)` for each, and collects results into a dict keyed by the path string
4. Error handling: fail-fast on the first error (raise immediately). No error collection -- keep it simple. If a consumer wants error tolerance, they can call `read()` in their own loop with `try/except`
5. If `paths` is empty, return an empty dict

### Inputs/Props

```python
@classmethod
def read_many(
    cls,
    paths: List[str],
    *,
    version: Optional[str] = None,
) -> Dict[str, "RegisterFile"]:  # or BlockFile / SectionFile
```

- `paths`: list of file path strings (must be valid file paths, not raw content)
- `version`: optional version string, passed through to each `read()` call

### Outputs/Behavior

- Returns `Dict[str, FileInstance]` where keys are the path strings from `paths` and values are the read file instances
- Order of dict matches input order (Python 3.7+ dict ordering)
- Each file is read independently -- no shared state between reads
- The version parameter applies uniformly to all files in the batch

### Error Handling

- If any `read()` call raises (e.g., `FileNotFoundError`, `EncodingWarning`, `UnicodeDecodeError`), it propagates immediately
- No partial results are returned on error
- `paths` validation: each element must be a string; no type coercion

## Acceptance Criteria

- [ ] Given `VersionedRegisterFile` with `VERSIONS = {"v1": [A], "v2": [B]}`, when `VersionedRegisterFile.read_many(["file1.dat", "file2.dat"], version="v1")` is called with valid file content, then a dict with 2 entries is returned, keyed by `"file1.dat"` and `"file2.dat"`, and both instances were parsed with version `"v1"` components
- [ ] Given the same setup, when `read_many(["file1.dat", "file2.dat"])` is called without `version`, then `cls.REGISTERS` is used (default behavior)
- [ ] Given `read_many([])`, when called, then an empty dict `{}` is returned
- [ ] Given a path list where the second file does not exist, when `read_many(["valid.dat", "missing.dat"])` is called, then `FileNotFoundError` is raised (fail-fast)
- [ ] Given the same `read_many` API on `BlockFile` and `SectionFile`, when tested, then identical behavior is observed
- [ ] Given `VersionedRegisterFile.REGISTERS == [B]`, when `read_many(paths, version="v1")` is called and returns, then `VersionedRegisterFile.REGISTERS` is still `[B]` (no class mutation)
- [ ] Given the existing test suite, when `pytest` is run, then all existing tests still pass

## Implementation Guide

### Suggested Approach

1. In `cfinterface/files/registerfile.py`, add after the `write()` method:

```python
@classmethod
def read_many(
    cls,
    paths: List[str],
    *,
    version: Optional[str] = None,
) -> Dict[str, "RegisterFile"]:
    """
    Reads multiple files with shared settings.

    :param paths: List of file paths to read
    :type paths: List[str]
    :param version: Optional schema version for all files
    :type version: str | None
    :return: Dict mapping each path to its read file instance
    :rtype: Dict[str, RegisterFile]
    """
    return {path: cls.read(path, version=version) for path in paths}
```

2. Repeat identically for `blockfile.py` and `sectionfile.py`, adjusting the return type annotation
3. Add tests in the existing test files

### Key Files to Modify

- `cfinterface/files/registerfile.py` -- add `read_many()` classmethod
- `cfinterface/files/blockfile.py` -- add `read_many()` classmethod
- `cfinterface/files/sectionfile.py` -- add `read_many()` classmethod
- `tests/files/test_registerfile.py` -- add tests for `read_many()`
- `tests/files/test_blockfile.py` -- add tests for `read_many()`
- `tests/files/test_sectionfile.py` -- add tests for `read_many()`

### Patterns to Follow

- `read()` classmethod pattern -- `read_many()` delegates entirely to `read()`, no custom parsing logic
- Dict comprehension for the implementation -- keeps it minimal and readable
- Numpydoc docstring style matching the existing `read()` and `write()` docstrings

### Pitfalls to Avoid

- Do NOT add `concurrent.futures` or any parallel execution -- the consumer can add parallelism if needed; the framework should stay simple and predictable
- Do NOT add error collection (`errors: List[Exception]`) -- fail-fast is the correct default for a file parsing library; error tolerance belongs in the consumer
- Do NOT accept `Union[str, bytes]` in `paths` -- `read_many()` is for file paths only; raw content buffers should use `read()` directly
- Do NOT add `encoding` override parameter -- the `ENCODING` class attribute already handles encoding fallback; adding another knob increases API surface without clear benefit
- The return type annotation uses a string literal `"RegisterFile"` to avoid circular import issues and forward reference problems

## Testing Requirements

### Unit Tests

- Test `read_many()` with 2 valid file paths (mock or buffer-based), verify dict keys and instance types
- Test `read_many([])` returns empty dict
- Test `read_many()` with `version` parameter passes version through to each `read()` call
- Test `read_many()` does not mutate class-level component list
- Test `read_many()` with invalid path raises `FileNotFoundError` or `EncodingWarning`
- All the above for all three file classes

### Integration Tests

- Test `read_many()` with the versioned file subclasses (`VersionedRegisterFile`, `VersionedBlockFile`, `VersionedSectionFile`) and version parameter

### E2E Tests (if applicable)

Not applicable.

## Dependencies

- **Blocked By**: ticket-025 (needs `version` parameter on `read()`)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
