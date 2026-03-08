# ticket-009 Create v1.8-to-v1.9 migration guide

## Context

### Background

cfinterface v1.9.0 introduces several breaking changes and new features: pandas becomes optional, `StorageType` enum replaces bare strings, `set_version()` is deprecated in favor of `version=` keyword argument, `TabularParser` is added, `read_many()` batch API is added, and data containers are migrated from linked lists to arrays. Downstream users need a step-by-step migration guide to update their code from v1.8.x to v1.9.0.

### Relation to Epic

Epic 03 creates five documentation content pages. This ticket produces the migration guide, which is critical for adoption of v1.9.0 by existing users. It references changes documented in `CHANGELOG.md` but presents them in a tutorial-like, step-by-step format with before/after code examples.

### Current State

- `CHANGELOG.md` at the repository root documents all v1.9.0 changes in Added/Changed/Deprecated/Fixed sections
- `docs/source/guides/` directory will be created by ticket-007 (or this ticket if executed first)
- `docs/source/conf.py` has `language = "pt_BR"` and Furo theme
- Key breaking changes from CHANGELOG.md:
  - pandas moved to optional dependency (`pip install cfinterface[pandas]`)
  - `StorageType` enum replaces `"TEXT"`/`"BINARY"` strings (deprecation warning emitted)
  - `set_version()` deprecated; use `version=` keyword in `read()`
  - Data containers (RegisterData, BlockData, SectionData) changed from linked lists to array-backed lists
  - `previous`/`next` on Register/Block/Section are now computed properties

## Specification

### Requirements

1. Create `docs/source/guides/migration-v1.9.rst` in pt-BR containing:
   - Title: "Guia de Migracao: v1.8.x para v1.9.0"
   - Introduction explaining the scope of changes and that this guide covers all breaking changes and deprecations
   - Section "pandas como Dependencia Opcional" with before/after:
     - Before: `pip install cfinterface` (pandas included)
     - After: `pip install cfinterface[pandas]` (only if needed)
     - Code change: imports that assumed pandas was available must be guarded or the `[pandas]` extra must be installed
   - Section "StorageType Enum" with before/after:
     - Before: `STORAGE = "TEXT"` / `STORAGE = "BINARY"`
     - After: `STORAGE = StorageType.TEXT` / `STORAGE = StorageType.BINARY`
     - Note the deprecation warning for bare strings
   - Section "Deprecacao de set_version()" with before/after:
     - Before: `file.set_version("1.0"); file.read("path.txt")`
     - After: `file.read("path.txt", version="1.0")`
   - Section "Containers Baseados em Array" explaining the migration from linked-list to array-backed containers:
     - `previous`/`next` are now computed properties, not stored pointers
     - `len()` is now O(1)
     - Type-indexed lookups via `data.of_type(MyRegister)` remain the primary access pattern
   - Section "Novas Funcionalidades" briefly listing what is new (not breaking) for users who want to adopt:
     - `TabularParser` and `ColumnDef` for schema-driven tabular parsing
     - `read_many()` batch API on file classes
     - `SchemaVersion` and `validate_version()` for multi-version file schemas
     - `py.typed` marker for PEP 561 compliance
   - Section "Checklist de Migracao" with a numbered list of steps to migrate a downstream project

### Inputs/Props

- `CHANGELOG.md` content for accurate change descriptions
- Source code for accurate class/method signatures

### Outputs/Behavior

- A single RST file at `docs/source/guides/migration-v1.9.rst` that renders without Sphinx warnings
- Before/after code examples use `.. code-block:: python`
- All prose in pt-BR

### Error Handling

- N/A (documentation page)

## Acceptance Criteria

- [ ] Given the ticket is implemented, when checking `docs/source/guides/migration-v1.9.rst`, then the file exists and contains the title "Guia de Migracao: v1.8.x para v1.9.0"
- [ ] Given `docs/source/guides/migration-v1.9.rst` exists, when searching for `.. code-block:: python`, then at least 6 code blocks are present (before/after pairs for pandas, StorageType, and set_version deprecation)
- [ ] Given `docs/source/guides/migration-v1.9.rst` exists, when searching for section headers, then the file contains at least these 5 sections: "pandas como Dependencia Opcional", "StorageType Enum", "Deprecacao de set_version()", "Containers Baseados em Array", "Checklist de Migracao"
- [ ] Given `docs/source/guides/migration-v1.9.rst` exists, when running `sphinx-build -W -b html docs/source docs/build/html`, then the build completes with exit code 0

## Implementation Guide

### Suggested Approach

1. Create `docs/source/guides/` directory if it does not exist
2. Create `docs/source/guides/migration-v1.9.rst` with the title
3. Write the introduction paragraph explaining that v1.9.0 is a feature release with some breaking changes for downstream users
4. For each breaking change section, use a consistent format:
   - Brief explanation of what changed and why
   - "Antes (v1.8.x):" code block
   - "Depois (v1.9.0):" code block
5. For the "Novas Funcionalidades" section, write brief descriptions with links to API reference docs using `:class:` and `:func:` roles
6. For the "Checklist de Migracao" section, write a numbered RST list:
   1. Atualizar `pip install cfinterface[pandas]` se pandas for necessario
   2. Substituir `STORAGE = "TEXT"` por `STORAGE = StorageType.TEXT`
   3. Substituir `set_version()` por argumento `version=` em `read()`
   4. Verificar codigo que depende de `previous`/`next` como atributos armazenados
   5. Executar testes para verificar compatibilidade
7. Do NOT modify `index.rst`

### Key Files to Modify

- `docs/source/guides/migration-v1.9.rst` (CREATE)

### Patterns to Follow

- RST section hierarchy: `=` for title, `-` for sections, `~` for subsections
- `.. code-block:: python` for all code examples
- Before/after pattern with clear labels ("Antes (v1.8.x):" and "Depois (v1.9.0):")
- `:class:` / `:func:` roles for API references
- All prose in pt-BR

### Pitfalls to Avoid

- Do NOT add toctree entry to `index.rst` -- ticket-013 handles that
- Do NOT duplicate the entire CHANGELOG -- present information in a tutorial-like migration format
- Do NOT show deprecated patterns as recommended usage -- always show the v1.9.0 way as the "after"
- Do NOT include automated migration scripts -- manual instructions only

## Testing Requirements

### Unit Tests

- N/A (documentation content)

### Integration Tests

- Run `sphinx-build -W -b html docs/source docs/build/html` and verify exit code 0
- Verify `docs/build/html/guides/migration-v1.9.html` exists

### E2E Tests

- N/A

## Dependencies

- **Blocked By**: ticket-006-update-conf-language-intersphinx.md
- **Blocks**: ticket-013-restructure-index-rst.md

## Effort Estimate

**Points**: 2
**Confidence**: High
