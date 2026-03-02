# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.9.0] - Unreleased

### Added

- `StorageType` enum (`cfinterface/storage.py`) for type-safe `TEXT`/`BINARY` dispatch, replacing bare string literals
- `TabularParser` class (`cfinterface/components/tabular.py`) for generic, schema-driven tabular file parsing
- `TabularSection` convenience base class for sections backed by a tabular data block
- `ColumnDef` named tuple for declaring column schemas (name, width, dtype, default) in `TabularParser`
- Delimited tabular parsing support (CSV-style, semicolon-separated, and custom delimiters) in `TabularParser`
- `SchemaVersion` descriptor (`cfinterface/versioning.py`) for declarative version binding on file classes
- `resolve_version()` utility function for resolving the active schema version at read/write time
- `VersionMatchResult` named tuple for structured version comparison results
- `validate_version()` function for detecting version mismatches between file schema and actual content
- `read_many()` batch read API on `RegisterFile`, `BlockFile`, and `SectionFile` for reading multiple files in one call
- `validate()` method on file classes for programmatic version mismatch detection
- `py.typed` marker file for PEP 561 compliance, enabling downstream type checking of cfinterface
- Hypothesis property-based tests for `Field` round-trip correctness (`tests/components/test_field_hypothesis.py`)
- Hypothesis property-based tests for `TabularParser` parsing invariants (`tests/components/test_tabular_hypothesis.py`)
- pytest-benchmark integration for performance regression testing (`tests/components/test_floatfield_benchmark.py`)
- Sphinx reference documentation for `TabularParser`, versioning module, `StorageType`, and adapter classes
- CI test matrix covering Python 3.10, 3.11, 3.12, 3.13, and 3.14 on Linux, plus Python 3.12 on Windows
- Separated lint/quality CI job running mypy, ruff, ty (informational), and `sphinx-build -W`
- Manual-dispatch benchmark CI workflow (`.github/workflows/benchmark.yml`) for on-demand performance profiling

### Changed

- pandas moved from required to optional dependency; install via `pip install cfinterface[pandas]`
- Only `numpy>=2.0.0` remains as a hard runtime dependency
- Regex patterns in the adapter layer are now compiled and cached at first use via `_pattern_cache`, eliminating per-call recompilation
- `FloatField._textual_write()` optimized from an O(decimal_digits) trial loop to at most 3 format attempts
- `RegisterData`, `BlockData`, and `SectionData` migrated from linked-list structures to array-backed (`list`) containers with O(1) `len()` and type-indexed lookups
- `Register.previous`/`next`, `Block.previous`/`next`, and `Section.previous`/`next` are now computed properties derived from container position instead of stored linked-list pointers
- `Field.read()` and `Field.write()` use `@overload` signatures for type-safe `str`/`bytes` dispatch
- All four adapter `factory()` functions accept `StorageType` enum values in addition to legacy string values
- `RegisterFile`, `BlockFile`, and `SectionFile` `STORAGE` class attribute defaults changed to `StorageType.TEXT`
- pyproject.toml expanded with `[tool.mypy]`, `[tool.pytest.ini_options]`, `[tool.coverage]`, and an expanded `[tool.ruff.lint]` section
- Python classifiers updated to include 3.10, 3.11, 3.12, 3.13, and 3.14
- `docs.yml` and `publish.yml` GitHub Actions workflows modernized to use `uv` and consistent job patterns

### Deprecated

- Passing `"TEXT"` or `"BINARY"` as plain strings to the file class `STORAGE` attribute; use `StorageType.TEXT` or `StorageType.BINARY` instead (a deprecation warning is emitted at file class instantiation time)
- `set_version()` method on file classes; pass the `version=` keyword argument to `read()` instead

### Fixed

- Null value detection in `Field` write methods now uses `math.isnan()` instead of `pd.isnull()`, eliminating the unnecessary pandas import at module level
- `RegisterFile._as_df()` now performs a lazy pandas import, only importing the library when the method is actually called

[Unreleased]: https://github.com/rjmalves/cfinterface/compare/v1.9.0...HEAD
[1.9.0]: https://github.com/rjmalves/cfinterface/compare/v1.8.3...v1.9.0
