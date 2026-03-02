# Epic 04: Sphinx Documentation for New Features

## Goal

Create comprehensive Sphinx reference documentation for all features introduced in the architecture overhaul, fix missing docstrings, and ensure the documentation builds cleanly with `-W` (warnings as errors).

## Scope

- Add reference pages for TabularParser, TabularSection, ColumnDef
- Add reference page for versioning module (SchemaVersion, resolve_version, validate_version, VersionMatchResult)
- Add reference page for StorageType enum
- Add reference pages for adapter layer (repository pattern)
- Add docstring to RegisterFile.read_many()
- Update index.rst toctree to include new reference sections
- Ensure sphinx-build -W passes with zero warnings

## Out of Scope

- Sphinx gallery examples (examples/ directory is out of scope)
- Tutorial content updates
- Getting started guide updates
- API redesign or new features

## Dependencies

- **Epic 1** must be completed (py.typed, mypy config may affect autodoc)
- Epics 2-3 are independent (documentation does not depend on CI or test infrastructure)

## Tickets

1. **ticket-015-add-tabular-reference-pages** — Create Sphinx reference pages for TabularParser, TabularSection, ColumnDef
2. **ticket-016-add-versioning-reference-page** — Create Sphinx reference page for versioning module
3. **ticket-017-add-storage-and-adapter-pages** — Create Sphinx reference pages for StorageType and adapter layer
4. **ticket-018-fix-docstrings-and-index** — Add missing docstrings and update index.rst toctree

## Success Criteria

- sphinx-build -W passes with zero warnings
- All new features have autodoc reference pages accessible from the documentation
- RegisterFile.read_many() has a complete docstring
- index.rst toctree includes all new reference sections
