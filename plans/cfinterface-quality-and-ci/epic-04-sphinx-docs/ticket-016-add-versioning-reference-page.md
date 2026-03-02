# ticket-016 Create Sphinx Reference Page for Versioning Module

## Context

### Background

The architecture overhaul introduced a versioning module at `cfinterface/versioning.py` that enables forward-compatible file format handling. It exports four public names: `SchemaVersion` (NamedTuple), `VersionMatchResult` (NamedTuple), `resolve_version` (function), and `validate_version` (function). All four are re-exported from `cfinterface/__init__.py`. These have numpydoc-style docstrings but no Sphinx reference page.

### Relation to Epic

This is the second ticket in Epic 04. It creates the versioning reference section that will be integrated into the main toctree by ticket-018. This ticket is independent of tickets 015 and 017 and can be implemented in parallel with them.

### Current State

The existing documentation reference structure under `docs/source/reference/` has five subdirectories (`blocks/`, `fields/`, `line/`, `registers/`, `sections/`). There is no `docs/source/reference/versioning/` directory. The source module `cfinterface/versioning.py` contains all four public names in a single flat file (no subpackage).

## Specification

### Requirements

1. Create directory `docs/source/reference/versioning/` with a `files/` subdirectory
2. Create `docs/source/reference/versioning/index.rst` following the established pattern
3. Create `docs/source/reference/versioning/files/versioning.rst` documenting all four public names from `cfinterface.versioning` on a single page: `SchemaVersion`, `VersionMatchResult`, `resolve_version`, `validate_version`
4. Use `.. autoclass::` for the NamedTuples and `.. autofunction::` for the functions

### Inputs/Props

- Source module: `cfinterface.versioning`
- Types to document: `SchemaVersion` (NamedTuple), `VersionMatchResult` (NamedTuple)
- Functions to document: `resolve_version`, `validate_version`

### Outputs/Behavior

- Two new `.rst` files are created and render correctly with `sphinx-build`
- All four public names from `cfinterface.versioning` appear on a single reference page since they are all part of one cohesive module
- NamedTuple fields (`key`, `components`, `description` for `SchemaVersion`; `matched`, `expected_types`, `found_types`, `missing_types`, `unexpected_types`, `default_ratio` for `VersionMatchResult`) are rendered via autodoc

### Error Handling

Not applicable (static documentation files).

## Acceptance Criteria

- [ ] Given the file `docs/source/reference/versioning/index.rst` exists, when its content is inspected, then it contains a `.. _versioning:` label, a "Versioning" heading, and a `toctree` directive listing `files/versioning`
- [ ] Given the file `docs/source/reference/versioning/files/versioning.rst` exists, when its content is inspected, then it contains `.. currentmodule:: cfinterface.versioning`, `.. autoclass:: SchemaVersion` with `:members:`, `.. autoclass:: VersionMatchResult` with `:members:`, `.. autofunction:: resolve_version`, and `.. autofunction:: validate_version`
- [ ] Given these two files are created, when `sphinx-build -b html docs/source docs/build` is run (without `-W`), then the versioning page is generated in the output without errors related to the versioning module

## Implementation Guide

### Suggested Approach

1. Create the directory structure: `docs/source/reference/versioning/files/`
2. Create `docs/source/reference/versioning/index.rst`:

   ```rst
   .. _versioning:

   Versioning
   ============

   .. toctree::
      :maxdepth: 1

      files/versioning
   ```

3. Create `docs/source/reference/versioning/files/versioning.rst`. Since this module has four public names (two NamedTuples and two functions), use separate labels for each and use `.. autoclass::` for NamedTuples and `.. autofunction::` for functions:

   ```rst
   .. _schemaversion:

   SchemaVersion
   ==============

   .. currentmodule:: cfinterface.versioning

   .. autoclass:: SchemaVersion
      :members:


   .. _versionmatchresult:

   VersionMatchResult
   ===================

   .. currentmodule:: cfinterface.versioning

   .. autoclass:: VersionMatchResult
      :members:


   .. _resolve_version:

   resolve_version
   =================

   .. currentmodule:: cfinterface.versioning

   .. autofunction:: resolve_version


   .. _validate_version:

   validate_version
   ==================

   .. currentmodule:: cfinterface.versioning

   .. autofunction:: validate_version
   ```

### Key Files to Modify

- `docs/source/reference/versioning/index.rst` (create)
- `docs/source/reference/versioning/files/versioning.rst` (create)

### Patterns to Follow

- Use the exact same RST structure as `docs/source/reference/sections/index.rst` for the index
- Use the same multi-item-per-page pattern as `docs/source/reference/blocks/files/block.rst` (which documents `Block` and `DefaultBlock` on a single page with separate labels)
- For functions, use `.. autofunction::` instead of `.. autoclass::` (this is the standard Sphinx autodoc directive for standalone functions)

### Pitfalls to Avoid

- Do NOT add the versioning reference to `docs/source/index.rst` toctree in this ticket; that is handled by ticket-018
- Do NOT modify any Python source files; this ticket is purely about creating `.rst` files
- Do NOT document private functions or implementation details

## Testing Requirements

### Unit Tests

Not applicable (static documentation files).

### Integration Tests

Run `sphinx-build -b html docs/source docs/build` and verify the versioning page appears in the build output without errors referencing the versioning module. A toctree warning is expected since `index.rst` is not yet updated.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-004-fix-mypy-strict-errors.md (type annotations must be correct for autodoc; already completed)
- **Blocks**: ticket-018-fix-docstrings-and-index.md (index.rst updates depend on this reference section existing)

## Effort Estimate

**Points**: 1
**Confidence**: High
