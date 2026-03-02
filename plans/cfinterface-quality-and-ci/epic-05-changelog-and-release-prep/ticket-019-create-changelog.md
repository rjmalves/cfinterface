# ticket-019 Create CHANGELOG.md for v1.9.0

## Context

### Background

The cfinterface project has undergone two major improvement plans since its v1.8.3 release: a 7-epic architecture overhaul (27 tickets) and a 5-epic quality/CI plan (20 tickets). These changes span pandas removal, StorageType enum, FloatField optimization, array-backed data containers, type-safe text/binary dispatch, generic tabular parser, schema versioning, pyproject hardening, CI modernization, property-based testing, and Sphinx documentation. Despite the scope of these changes, the project has never had a CHANGELOG.md. This ticket creates one, starting with v1.9.0.

### Relation to Epic

This is the first ticket in Epic 05 (CHANGELOG and Release Preparation). The CHANGELOG must exist before ticket-020 can perform its version consistency review.

### Current State

- No `CHANGELOG.md` exists at the repository root.
- The version in `cfinterface/__init__.py` is `"1.9.0"`.
- The latest git tag is `v1.8.3`.
- All architecture overhaul changes (epics 01-07, 27 tickets) and quality/CI changes (epics 01-04, 18 tickets) are committed on the `feat/cfinterface-quality-and-ci` branch.

## Specification

### Requirements

1. Create `CHANGELOG.md` at the repository root following the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
2. Include a header stating the project adheres to Keep a Changelog and Semantic Versioning.
3. Include an `[Unreleased]` section (empty, as a placeholder for future work).
4. Include a `[1.9.0]` section with date set to `Unreleased` (the maintainer will set the actual release date).
5. Organize v1.9.0 changes under the standard Keep a Changelog categories: **Added**, **Changed**, **Deprecated**, **Fixed**.
6. Document all changes from the architecture overhaul plan (7 epics, 27 tickets) and the quality/CI plan (epics 01-04, 18 tickets) under the appropriate categories.

### Content Categorization

The following changes must appear under their respective Keep a Changelog categories:

**Added:**

- `StorageType` enum (`cfinterface/storage.py`) for type-safe TEXT/BINARY dispatch
- `TabularParser` and `TabularSection` classes for generic tabular file parsing (`cfinterface/components/tabular.py`)
- `ColumnDef` named tuple for declaring tabular column schemas
- Delimited tabular parsing support (CSV-style, semicolon, etc.)
- `SchemaVersion` descriptor and `resolve_version()` for schema versioning (`cfinterface/versioning.py`)
- `VersionMatchResult` named tuple and `validate_version()` for version validation
- `read_many()` batch read API on `RegisterFile`, `BlockFile`, `SectionFile`
- `validate()` method on file classes for version mismatch detection
- `py.typed` marker for PEP 561 compliance
- Hypothesis property-based tests for field round-trips and tabular parsing
- pytest-benchmark integration for performance regression testing
- Sphinx reference documentation for TabularParser, versioning, StorageType, and adapters
- CI test matrix: Python 3.10-3.14 on Linux, 3.12 on Windows
- Separated lint/quality CI job with mypy, ruff, ty (informational), and sphinx -W
- Manual-dispatch benchmark CI workflow

**Changed:**

- pandas moved from required to optional dependency (install via `pip install cfinterface[pandas]`)
- Only `numpy>=2.0.0` remains as a hard runtime dependency
- Regex patterns in adapter layer are now compiled and cached at first use (`_pattern_cache`)
- `FloatField._textual_write()` optimized from O(decimal_digits) loop to at most 3 format attempts
- `RegisterData`, `BlockData`, `SectionData` migrated from linked lists to array-backed (`list`) containers with O(1) `len()` and type-indexed lookups
- `Register.previous`/`next`, `Block.previous`/`next`, `Section.previous`/`next` are now computed properties from container position instead of stored linked-list pointers
- `Field.read()`/`write()` use `@overload` for type-safe `str`/`bytes` dispatch
- All four adapter `factory()` functions accept `StorageType` enum in addition to string values
- `RegisterFile`, `BlockFile`, `SectionFile` `STORAGE` defaults changed to `StorageType.TEXT`
- pyproject.toml expanded with `[tool.mypy]`, `[tool.pytest.ini_options]`, `[tool.coverage]`, and expanded `[tool.ruff.lint]` configuration
- Python classifiers updated to include 3.10, 3.11, 3.12, 3.13, 3.14
- docs.yml and publish.yml workflows modernized with uv and consistent patterns

**Deprecated:**

- Passing `"TEXT"` or `"BINARY"` as plain strings to file class `STORAGE` attribute (use `StorageType.TEXT`/`StorageType.BINARY` instead; deprecation warning emitted at file class `__init__` time)
- `set_version()` method on file classes (pass `version=` keyword argument to `read()` instead)

**Fixed:**

- Null value detection in field write methods now uses native `math.isnan()` instead of `pd.isnull()`, eliminating unnecessary pandas import at module level
- `RegisterFile._as_df()` now uses lazy pandas import, only importing when actually called

### Formatting Rules

- Use Markdown headings: `# Changelog`, `## [Unreleased]`, `## [1.9.0] - Unreleased`, `### Added`, etc.
- Each change entry is a bullet point (`-`) with a concise one-line description.
- Group entries logically within each category (architecture changes first, then quality/CI changes).
- Do not include links to PRs or commits (the project does not use a consistent PR-per-change workflow).
- Include comparison links at the bottom of the file: `[Unreleased]` comparing to `v1.9.0`, `[1.9.0]` comparing to `v1.8.3`.

### Inputs/Props

- Git history from `v1.8.3` to current HEAD.
- Architecture improvement plan README (`plans/cfinterface-architecture-improvement/README.md`) for epic/ticket reference.
- Quality/CI plan README (`plans/cfinterface-quality-and-ci/README.md`) for epic/ticket reference.

### Outputs/Behavior

A single file `CHANGELOG.md` at the repository root, containing the full v1.9.0 changelog in Keep a Changelog format.

### Error Handling

Not applicable (this is a documentation-only ticket creating a static file).

## Acceptance Criteria

- [ ] Given the repository root, when listing files, then `CHANGELOG.md` exists at `/home/rogerio/git/cfinterface/CHANGELOG.md`.
- [ ] Given `CHANGELOG.md`, when reading its first 5 lines, then it contains `# Changelog` as the top-level heading and a line stating adherence to Keep a Changelog and Semantic Versioning.
- [ ] Given `CHANGELOG.md`, when searching for section headers, then it contains both `## [Unreleased]` and `## [1.9.0] - Unreleased` sections.
- [ ] Given the `## [1.9.0]` section, when examining its subsections, then it contains `### Added`, `### Changed`, `### Deprecated`, and `### Fixed` subsections.
- [ ] Given the `### Added` subsection, when counting bullet points, then it contains at least 14 entries covering StorageType, TabularParser, TabularSection, ColumnDef, delimited parsing, SchemaVersion, resolve_version, VersionMatchResult, validate_version, read_many, validate, py.typed, hypothesis tests, pytest-benchmark, Sphinx docs, CI matrix, lint job, and benchmark workflow.

## Implementation Guide

### Suggested Approach

1. Create `CHANGELOG.md` at the repository root.
2. Write the standard Keep a Changelog header with project name and format adherence note.
3. Add an empty `## [Unreleased]` section.
4. Add the `## [1.9.0] - Unreleased` section.
5. Under `### Added`, list all new public APIs, modules, and infrastructure introduced in v1.9.0 (StorageType, TabularParser, TabularSection, ColumnDef, versioning module, batch API, CI workflows, testing infrastructure, documentation).
6. Under `### Changed`, list all modifications to existing behavior (pandas optional, regex caching, FloatField optimization, array-backed containers, computed properties, type-safe overloads, factory function signatures, pyproject config, classifiers, CI workflows).
7. Under `### Deprecated`, list the string-based STORAGE parameter and `set_version()` method.
8. Under `### Fixed`, list the null detection fix and lazy pandas import.
9. Add comparison links at the bottom referencing the GitHub repository URL `https://github.com/rjmalves/cfinterface/`.

### Key Files to Modify

- `CHANGELOG.md` (create new file at repository root)

### Patterns to Follow

- Follow the Keep a Changelog format exactly as specified at https://keepachangelog.com/en/1.1.0/.
- Use the same concise, technical tone found in the project's existing documentation and commit messages.
- Reference module paths (e.g., `cfinterface/versioning.py`) or class names (e.g., `TabularParser`) where it helps the reader locate the change.

### Pitfalls to Avoid

- Do not set a specific release date for v1.9.0; use `Unreleased` as the date placeholder. The maintainer will set the actual date.
- Do not include changes from before v1.9.0 (the CHANGELOG starts fresh with this version).
- Do not include links to individual PRs or commits.
- Do not duplicate entries across categories (e.g., pandas removal is a "Changed" item, not also an "Added" item).
- Do not include internal implementation details that are not user-facing (e.g., `_pattern_cache` internals, `_refresh_indices` method details).

### Out of Scope

- Changes from versions prior to v1.9.0 (the CHANGELOG starts with v1.9.0 only).
- Modifying any Python source files, CI workflows, or documentation pages.

## Testing Requirements

### Unit Tests

Not applicable (no code changes).

### Integration Tests

Not applicable (no code changes).

### Manual Verification

- Open `CHANGELOG.md` and verify it follows the Keep a Changelog format.
- Verify all four categories (Added, Changed, Deprecated, Fixed) are present under v1.9.0.
- Cross-reference entries against the architecture improvement README (27 tickets across 7 epics) and quality/CI README (18 tickets across 4 epics) to confirm completeness.

## Dependencies

- **Blocked By**: ticket-015-add-tabular-reference-pages.md, ticket-016-add-versioning-reference-page.md, ticket-017-add-storage-and-adapter-pages.md, ticket-018-fix-docstrings-and-index.md (all documentation must be complete so all changes can be documented)
- **Blocks**: ticket-020-release-prep-review.md

## Effort Estimate

**Points**: 2
**Confidence**: High
