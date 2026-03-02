# ticket-017 Create Sphinx Reference Pages for StorageType and Adapters

## Context

### Background

The architecture overhaul introduced a `StorageType` enum in `cfinterface/storage.py` and an adapter layer under `cfinterface/adapters/` implementing the repository pattern for I/O dispatch. `StorageType` is a public API exported from `cfinterface/__init__.py` that determines text vs. binary file handling. The adapter layer contains three repository subsystems (components, reading, writing) that are internal infrastructure but should be documented for contributors and advanced users.

### Relation to Epic

This is the third ticket in Epic 04. It creates the storage and adapter reference sections that will be integrated into the main toctree by ticket-018. This ticket is independent of tickets 015 and 016 and can be implemented in parallel with them.

### Current State

The existing documentation reference structure under `docs/source/reference/` has five subdirectories. There is no `docs/source/reference/storage/` or `docs/source/reference/adapters/` directory.

The adapter layer has this structure:

- `cfinterface/adapters/components/repository.py` -- ABC `Repository`, `BinaryRepository`, `TextualRepository`, `factory()` for pattern matching on lines
- `cfinterface/adapters/components/line/repository.py` -- ABC `Repository`, `TextualRepository`, `BinaryRepository`, `factory()` for reading/writing line fields
- `cfinterface/adapters/reading/repository.py` -- ABC `Repository`, `BinaryRepository`, `TextualRepository`, `factory()` for file reading
- `cfinterface/adapters/writing/repository.py` -- ABC `Repository`, `BinaryRepository`, `TextualRepository`, `factory()` for file writing

Each adapter submodule follows the same pattern: an ABC `Repository`, `BinaryRepository` and `TextualRepository` concrete classes, and a `factory()` function.

## Specification

### Requirements

1. Create `docs/source/reference/storage/` with `index.rst` and `files/storagetype.rst` documenting the `StorageType` enum from `cfinterface.storage`
2. Create `docs/source/reference/adapters/` with `index.rst` and individual `.rst` files for each of the four adapter repositories under a `files/` subdirectory
3. Document only the public classes and the `factory()` functions in each adapter module; do NOT document `_ensure_storage_type` (it is private API)
4. Name the adapter `.rst` files descriptively to distinguish the four identically-named `Repository` classes: `components.rst`, `line.rst`, `reading.rst`, `writing.rst`

### Inputs/Props

- Source modules:
  - `cfinterface.storage` -- `StorageType`
  - `cfinterface.adapters.components.repository` -- `Repository`, `BinaryRepository`, `TextualRepository`, `factory`
  - `cfinterface.adapters.components.line.repository` -- `Repository`, `TextualRepository`, `BinaryRepository`, `factory`
  - `cfinterface.adapters.reading.repository` -- `Repository`, `BinaryRepository`, `TextualRepository`, `factory`
  - `cfinterface.adapters.writing.repository` -- `Repository`, `BinaryRepository`, `TextualRepository`, `factory`

### Outputs/Behavior

- `StorageType` reference page shows the enum members (`TEXT`, `BINARY`) and the class docstring
- Each adapter page shows the ABC, both concrete implementations, and the `factory()` function
- Pages use `.. currentmodule::` to set the correct fully-qualified module path for each adapter submodule

### Error Handling

Not applicable (static documentation files).

## Acceptance Criteria

- [ ] Given the file `docs/source/reference/storage/index.rst` exists, when its content is inspected, then it contains a `.. _storage:` label, a "Storage" heading, and a `toctree` directive listing `files/storagetype`
- [ ] Given the file `docs/source/reference/storage/files/storagetype.rst` exists, when its content is inspected, then it contains `.. currentmodule:: cfinterface.storage` and `.. autoclass:: StorageType` with `:members:`
- [ ] Given the file `docs/source/reference/adapters/index.rst` exists, when its content is inspected, then it contains a `.. _adapters:` label, an "Adapters" heading, and a `toctree` directive listing `files/components`, `files/line`, `files/reading`, `files/writing`
- [ ] Given any adapter `.rst` file (e.g., `docs/source/reference/adapters/files/components.rst`) exists, when its content is inspected, then it uses `.. currentmodule::` with the correct fully-qualified module path (e.g., `cfinterface.adapters.components.repository`) and documents `Repository`, `BinaryRepository`, `TextualRepository` with `.. autoclass::` and `factory` with `.. autofunction::`

## Implementation Guide

### Suggested Approach

1. Create directory structures: `docs/source/reference/storage/files/` and `docs/source/reference/adapters/files/`

2. Create `docs/source/reference/storage/index.rst`:

   ```rst
   .. _storage:

   Storage
   ============

   .. toctree::
      :maxdepth: 1

      files/storagetype
   ```

3. Create `docs/source/reference/storage/files/storagetype.rst`:

   ```rst
   .. _storagetype:

   StorageType
   ============

   .. currentmodule:: cfinterface.storage

   .. autoclass:: StorageType
      :members:
   ```

4. Create `docs/source/reference/adapters/index.rst`:

   ```rst
   .. _adapters:

   Adapters
   ============

   .. toctree::
      :maxdepth: 1

      files/components
      files/line
      files/reading
      files/writing
   ```

5. Create four adapter `.rst` files. Each follows the same multi-class pattern. Example for `docs/source/reference/adapters/files/components.rst`:

   ```rst
   .. _adapter-components:

   Component Adapters
   ===================

   .. currentmodule:: cfinterface.adapters.components.repository

   .. autoclass:: Repository
      :members:

   .. autoclass:: BinaryRepository
      :members:

   .. autoclass:: TextualRepository
      :members:

   .. autofunction:: factory
   ```

   Repeat for `line.rst` (module: `cfinterface.adapters.components.line.repository`), `reading.rst` (module: `cfinterface.adapters.reading.repository`), and `writing.rst` (module: `cfinterface.adapters.writing.repository`), adjusting labels and headings accordingly (e.g., `.. _adapter-line:` / "Line Adapters", `.. _adapter-reading:` / "Reading Adapters", `.. _adapter-writing:` / "Writing Adapters").

### Key Files to Modify

- `docs/source/reference/storage/index.rst` (create)
- `docs/source/reference/storage/files/storagetype.rst` (create)
- `docs/source/reference/adapters/index.rst` (create)
- `docs/source/reference/adapters/files/components.rst` (create)
- `docs/source/reference/adapters/files/line.rst` (create)
- `docs/source/reference/adapters/files/reading.rst` (create)
- `docs/source/reference/adapters/files/writing.rst` (create)

### Patterns to Follow

- Use the exact same RST index structure as `docs/source/reference/sections/index.rst`
- Use the multi-class-per-page pattern from `docs/source/reference/blocks/files/block.rst`
- Use unique RST labels with `adapter-` prefix to avoid label collisions with adapter classes that share the same name (e.g., all four modules define `Repository`)

### Pitfalls to Avoid

- Do NOT add the storage or adapter references to `docs/source/index.rst` toctree; that is handled by ticket-018
- Do NOT document `_ensure_storage_type` from `cfinterface.storage` (private API with underscore prefix)
- Do NOT modify any Python source files
- Use distinct RST labels (`adapter-components`, `adapter-line`, `adapter-reading`, `adapter-writing`) to avoid Sphinx duplicate label warnings across the four identically-structured adapter pages

## Testing Requirements

### Unit Tests

Not applicable (static documentation files).

### Integration Tests

Run `sphinx-build -b html docs/source docs/build` and verify the storage and adapter pages appear in the build output without errors referencing these modules. Toctree warnings are expected since `index.rst` is not yet updated.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-004-fix-mypy-strict-errors.md (type annotations must be correct for autodoc; already completed)
- **Blocks**: ticket-018-fix-docstrings-and-index.md (index.rst updates depend on these reference sections existing)

## Effort Estimate

**Points**: 2
**Confidence**: High
