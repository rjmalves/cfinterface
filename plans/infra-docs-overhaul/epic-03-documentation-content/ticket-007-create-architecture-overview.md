# ticket-007 Create architecture overview page

## Context

### Background

cfinterface is a framework for designing low-level interfaces to complex text or binary files. It uses a layered component hierarchy: `Field` (smallest unit, reads/writes a fixed-width value) -> `Line` (ordered sequence of Fields) -> `Register`/`Block`/`Section` (mid-level components that operate on file I/O handles) -> `RegisterFile`/`BlockFile`/`SectionFile` (top-level file classes). An adapter layer mediates between components and storage backends (`TEXT`/`BINARY`). New in v1.9.0, `TabularParser` provides schema-driven tabular parsing, `StorageType` replaces bare strings, and a versioning module supports multi-version file schemas. No documentation page currently explains this architecture to users or downstream library developers.

### Relation to Epic

Epic 03 creates five new documentation content pages in pt-BR. This ticket produces the architecture overview, which is the most conceptually dense page and will be referenced by the FAQ (ticket-008) and performance tips (ticket-010) pages. It does not modify `index.rst` -- that is handled by ticket-013.

### Current State

- `docs/source/conf.py` has `language = "pt_BR"` and Furo theme (set in epic-02)
- `docs/source/index.rst` has toctree sections for Install, Getting Started, and Module Reference but no Guides section
- No `docs/source/guides/` directory exists yet
- The codebase structure is: `cfinterface/components/` (field.py, line.py, register.py, block.py, section.py, tabular.py), `cfinterface/files/` (registerfile.py, blockfile.py, sectionfile.py), `cfinterface/adapters/` (components/, reading/, writing/), `cfinterface/data/` (registerdata.py, blockdata.py, sectiondata.py), `cfinterface/storage.py`, `cfinterface/versioning.py`

## Specification

### Requirements

1. Create directory `docs/source/guides/`
2. Create `docs/source/guides/architecture.rst` in pt-BR containing:
   - Title: "Visao Geral da Arquitetura"
   - Introduction paragraph explaining cfinterface's purpose and design philosophy (declarative file parsing)
   - Section "Hierarquia de Componentes" with a text-based diagram (using RST `code-block:: text` or `.. code-block:: none`) showing the layered hierarchy: Field -> Line -> Register/Block/Section -> File classes
   - Section "Campos (Fields)" explaining Field, FloatField, IntegerField, LiteralField, DatetimeField and their role as atomic read/write units with fixed-width positional parsing
   - Section "Linha (Line)" explaining how Line aggregates Fields and delegates to the adapter layer
   - Section "Componentes Intermediarios" explaining Register (identifier-based line matching), Block (begin/end pattern matching), and Section (ordered file sections)
   - Section "Classes de Arquivo" explaining RegisterFile, BlockFile, SectionFile and their class attributes (REGISTERS/BLOCKS/SECTIONS, STORAGE, ENCODING, VERSIONS)
   - Section "Camada de Adaptadores" explaining the adapter/repository pattern that mediates between components and TEXT/BINARY storage
   - Section "TabularParser" explaining the schema-driven tabular parsing introduced in v1.9.0 with ColumnDef
   - Section "Versionamento" explaining SchemaVersion, resolve_version(), VERSIONS dict, and validate_version()
   - Section "StorageType" explaining the enum and deprecation of bare strings
   - Section "Pontos de Extensao" listing the extension points for downstream users: subclassing Field, Register, Block, Section; defining VERSIONS dicts; using TabularParser with custom ColumnDef schemas

### Inputs/Props

- Source code in `cfinterface/` package for accurate class/method names
- CHANGELOG.md for v1.9.0 feature descriptions

### Outputs/Behavior

- A single RST file at `docs/source/guides/architecture.rst` that renders without Sphinx warnings when built with `sphinx-build -W`
- The page must use proper RST cross-references (`:class:`, `:func:`, `:mod:`) where referencing cfinterface API objects
- All text content in pt-BR (titles, descriptions, explanations)
- Code examples in Python (code blocks are not translated)

### Error Handling

- N/A (documentation page, no runtime behavior)

## Acceptance Criteria

- [ ] Given the directory `docs/source/guides/` does not exist, when the ticket is implemented, then the directory `docs/source/guides/` exists and contains `architecture.rst`
- [ ] Given `docs/source/guides/architecture.rst` exists, when running `grep -c "Visao Geral da Arquitetura" docs/source/guides/architecture.rst`, then the output is `1` (title is present exactly once)
- [ ] Given `docs/source/guides/architecture.rst` exists, when searching for section headers, then the file contains all 9 sections: "Hierarquia de Componentes", "Campos (Fields)", "Linha (Line)", "Componentes Intermediarios", "Classes de Arquivo", "Camada de Adaptadores", "TabularParser", "Versionamento", "Pontos de Extensao"
- [ ] Given `docs/source/guides/architecture.rst` exists, when searching for a text-based hierarchy diagram, then the file contains a `.. code-block::` directive with at least Field, Line, Register, Block, Section, RegisterFile, BlockFile, SectionFile labels
- [ ] Given `docs/source/guides/architecture.rst` exists, when running `sphinx-build -W -b html docs/source docs/build/html`, then the build completes with exit code 0 and no warnings

## Implementation Guide

### Suggested Approach

1. Create the `docs/source/guides/` directory
2. Create `docs/source/guides/architecture.rst` with the title and introductory paragraph
3. Add the hierarchy diagram using `.. code-block:: text` showing the layered structure:
   ```
   Field (FloatField, IntegerField, LiteralField, DatetimeField)
     |
     v
   Line (sequencia ordenada de Fields)
     |
     v
   Register / Block / Section (componentes intermediarios)
     |
     v
   RegisterFile / BlockFile / SectionFile (classes de arquivo)
   ```
4. Write each section referencing the actual class attributes and method signatures from the codebase (e.g., `Register.IDENTIFIER`, `Register.IDENTIFIER_DIGITS`, `Register.LINE`, `Block.BEGIN_PATTERN`, `Block.END_PATTERN`, `Section.STORAGE`)
5. For the adapter section, explain the factory pattern in `cfinterface/adapters/components/repository.py` that dispatches to TEXT or BINARY implementations
6. For TabularParser, reference `ColumnDef` named tuple and the `parse_lines()`/`format_rows()` methods
7. For versioning, reference `SchemaVersion`, `resolve_version()`, `VERSIONS` dict pattern, and `validate_version()`
8. Use RST cross-references like `:class:\`cfinterface.components.field.Field\`` where appropriate
9. Do NOT modify `docs/source/index.rst` -- that is ticket-013's responsibility

### Key Files to Modify

- `docs/source/guides/architecture.rst` (CREATE)

### Patterns to Follow

- Use RST section hierarchy: `=` for title, `-` for sections, `~` for subsections (consistent with existing `tutorial.rst` and `contributing.rst`)
- Use `.. code-block:: python` for Python examples
- Use `.. code-block:: text` for diagrams
- Use `:class:`, `:func:`, `:mod:` roles for API cross-references
- All prose in pt-BR; code stays in English

### Pitfalls to Avoid

- Do NOT add a toctree entry to `index.rst` -- that is handled by ticket-013
- Do NOT create an `index.rst` inside `guides/` -- individual pages will be referenced directly from the root `index.rst`
- Do NOT use images or external diagram tools -- use text-based diagrams only
- Do NOT document private/internal APIs (methods starting with `_`) -- focus on the public API surface and extension points
- Do NOT use `StorageType` as `"TEXT"`/`"BINARY"` strings in examples -- always use the enum form

## Testing Requirements

### Unit Tests

- N/A (documentation content)

### Integration Tests

- Run `sphinx-build -W -b html docs/source docs/build/html` and verify exit code 0
- Verify the generated HTML file exists at `docs/build/html/guides/architecture.html`

### E2E Tests

- N/A

## Dependencies

- **Blocked By**: ticket-006-update-conf-language-intersphinx.md (conf.py must have pt_BR language set)
- **Blocks**: ticket-013-restructure-index-rst.md

## Effort Estimate

**Points**: 3
**Confidence**: High
