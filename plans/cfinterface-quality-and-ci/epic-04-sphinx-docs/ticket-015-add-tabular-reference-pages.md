# ticket-015 Create Sphinx Reference Pages for TabularParser

## Context

### Background

The architecture overhaul introduced a tabular parsing subsystem in `cfinterface/components/tabular.py` containing three public types: `ColumnDef` (NamedTuple), `TabularParser` (parser/formatter), and `TabularSection` (Section subclass for tabular data). These are fully functional with numpydoc-style docstrings, but have no Sphinx reference pages. This is the most significant documentation gap in the project because tabular parsing is a major new feature that users need to discover and learn.

### Relation to Epic

This is the first ticket in Epic 04 (Sphinx Documentation for New Features). It creates the tabular reference section that will later be integrated into the main toctree by ticket-018. Tickets 015-017 are independent and can be implemented in parallel; each creates a self-contained reference subdirectory.

### Current State

The existing documentation reference structure under `docs/source/reference/` has five subdirectories: `blocks/`, `fields/`, `line/`, `registers/`, and `sections/`. Each follows a consistent pattern:

- An `index.rst` with a label, heading, and `toctree` listing the individual `.rst` files
- Individual `.rst` files under a `files/` (or `components/`) subdirectory, each using `.. currentmodule::` and `.. autoclass::` directives

There is no `docs/source/reference/tabular/` directory. The source module `cfinterface/components/tabular.py` exports `ColumnDef`, `TabularParser`, and `TabularSection`.

## Specification

### Requirements

1. Create directory `docs/source/reference/tabular/` with an `index.rst` and a `files/` subdirectory
2. Create `docs/source/reference/tabular/index.rst` following the exact pattern used by `docs/source/reference/sections/index.rst`
3. Create `docs/source/reference/tabular/files/tabularparser.rst` documenting `TabularParser` and `ColumnDef` from `cfinterface.components.tabular`
4. Create `docs/source/reference/tabular/files/tabularsection.rst` documenting `TabularSection` from `cfinterface.components.tabular`
5. All `.rst` files must use the same autodoc pattern as existing reference pages (see Implementation Guide)

### Inputs/Props

- Source module: `cfinterface.components.tabular`
- Classes to document: `ColumnDef`, `TabularParser`, `TabularSection`
- Docstring format: numpydoc (already configured in `conf.py` via `numpydoc` extension)

### Outputs/Behavior

- Three new `.rst` files are created and render correctly with `sphinx-build`
- `ColumnDef` and `TabularParser` appear on the same page (they are tightly coupled: `ColumnDef` is only used as input to `TabularParser`)
- `TabularSection` gets its own page (it is a `Section` subclass with distinct semantics)
- All class members, including class attributes (`COLUMNS`, `HEADER_LINES`, `END_PATTERN`, `DELIMITER`, `STORAGE`) are rendered

### Error Handling

Not applicable (static documentation files).

## Acceptance Criteria

- [ ] Given the file `docs/source/reference/tabular/index.rst` exists, when its content is inspected, then it contains a `.. _tabular:` label, a "Tabular" heading, and a `toctree` directive listing `files/tabularparser` and `files/tabularsection`
- [ ] Given the file `docs/source/reference/tabular/files/tabularparser.rst` exists, when its content is inspected, then it contains `.. currentmodule:: cfinterface.components.tabular` and `.. autoclass:: ColumnDef` with `:members:` and `.. autoclass:: TabularParser` with `:members:`
- [ ] Given the file `docs/source/reference/tabular/files/tabularsection.rst` exists, when its content is inspected, then it contains `.. currentmodule:: cfinterface.components.tabular` and `.. autoclass:: TabularSection` with `:members:`
- [ ] Given these three files are created, when `sphinx-build -b html docs/source docs/build` is run (without `-W`), then the tabular pages are generated in the output without errors related to the tabular module

## Implementation Guide

### Suggested Approach

1. Create the directory structure: `docs/source/reference/tabular/files/`
2. Create `docs/source/reference/tabular/index.rst` following the exact pattern of `docs/source/reference/sections/index.rst`:

   ```rst
   .. _tabular:

   Tabular
   ============

   .. toctree::
      :maxdepth: 1

      files/tabularparser
      files/tabularsection
   ```

3. Create `docs/source/reference/tabular/files/tabularparser.rst` following the pattern of `docs/source/reference/blocks/files/block.rst` (which documents two classes on one page):

   ```rst
   .. _columndef:

   ColumnDef
   =========

   .. currentmodule:: cfinterface.components.tabular

   .. autoclass:: ColumnDef
      :members:


   .. _tabularparser:

   TabularParser
   ==============

   .. currentmodule:: cfinterface.components.tabular

   .. autoclass:: TabularParser
      :members:
   ```

4. Create `docs/source/reference/tabular/files/tabularsection.rst`:

   ```rst
   .. _tabularsection:

   TabularSection
   ===============

   .. currentmodule:: cfinterface.components.tabular

   .. autoclass:: TabularSection
      :members:
   ```

### Key Files to Modify

- `docs/source/reference/tabular/index.rst` (create)
- `docs/source/reference/tabular/files/tabularparser.rst` (create)
- `docs/source/reference/tabular/files/tabularsection.rst` (create)

### Patterns to Follow

- Use the exact same RST structure as `docs/source/reference/sections/index.rst` for the index
- Use the exact same RST structure as `docs/source/reference/blocks/files/block.rst` for multi-class pages (two classes on one page with separate labels)
- Use the exact same RST structure as `docs/source/reference/sections/files/sectionfile.rst` for single-class pages

### Pitfalls to Avoid

- Do NOT add the tabular reference to `docs/source/index.rst` toctree in this ticket; that is handled by ticket-018
- Do NOT modify any Python source files; this ticket is purely about creating `.rst` files
- Do NOT create example code or tutorial content (out of scope per epic overview)

## Testing Requirements

### Unit Tests

Not applicable (static documentation files).

### Integration Tests

Run `sphinx-build -b html docs/source docs/build` and verify the tabular pages appear in the build output without errors referencing the tabular module. Note: the build may produce warnings about the pages not being in a toctree (since `index.rst` is not updated until ticket-018) -- this is expected and acceptable.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-004-fix-mypy-strict-errors.md (type annotations must be correct for autodoc to work; already completed)
- **Blocks**: ticket-018-fix-docstrings-and-index.md (index.rst updates depend on this reference section existing)

## Effort Estimate

**Points**: 1
**Confidence**: High
