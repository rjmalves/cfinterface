# ticket-013 Restructure index.rst with new documentation sections

## Context

### Background

Epic 03 created four new guide pages under `docs/source/guides/` (architecture, FAQ, migration, performance) and updated the contributing page. All four guide pages currently use the `:orphan:` directive on line 1 because they are not yet included in any toctree. This ticket integrates them into `index.rst` by adding new toctree sections and removing the `:orphan:` directives.

### Relation to Epic

This is the second and final ticket in Epic 04 (Repository Polish). It is the capstone ticket for the entire plan -- after this, all documentation pages are properly linked from the main index and the Sphinx build produces no warnings.

### Current State

The current `docs/source/index.rst` has three toctree sections:

1. **Install** -- contains `install/install.rst`
2. **Getting Started** -- contains `getting_started/tutorial`, `examples/index.rst`, `getting_started/contributing`
3. **Module Reference** -- contains 9 reference pages (fields, line, blocks, registers, sections, tabular, versioning, storage, adapters)

The four guide pages exist at:

- `docs/source/guides/architecture.rst` (line 1: `:orphan:`)
- `docs/source/guides/faq.rst` (line 1: `:orphan:`)
- `docs/source/guides/migration-v1.9.rst` (line 1: `:orphan:`)
- `docs/source/guides/performance.rst` (line 1: `:orphan:`)

The introductory text in `index.rst` is currently in English.

## Specification

### Requirements

1. **Add a "Guias" toctree section** to `docs/source/index.rst` between "Getting Started" and "Module Reference", containing entries for:
   - `guides/architecture`
   - `guides/performance`
   - `guides/migration-v1.9`
2. **Add a "Recursos" toctree section** to `docs/source/index.rst` after "Module Reference", containing:
   - `guides/faq`
3. **Remove the `:orphan:` directive** (line 1) from all four guide files:
   - `docs/source/guides/architecture.rst`
   - `docs/source/guides/faq.rst`
   - `docs/source/guides/migration-v1.9.rst`
   - `docs/source/guides/performance.rst`
4. **Translate the introductory paragraph** in `index.rst` from English to pt-BR.
5. **Rename the "Getting Started" caption** to "Primeiros Passos".
6. **Rename the "Install" caption** to "Instalacao".
7. **Rename the "Module Reference" caption** to "Referencia de Modulos".
8. The Sphinx build (`uv run sphinx-build -W -b html docs/source docs/build/html`) must complete with zero warnings.

### Inputs/Props

- Existing `docs/source/index.rst` (see Current State above for full content).
- Four guide RST files with `:orphan:` on line 1.

### Outputs/Behavior

- Updated `index.rst` with 5 toctree sections (Instalacao, Primeiros Passos, Guias, Referencia de Modulos, Recursos) and pt-BR intro text.
- Four guide files with `:orphan:` removed (each file's line 1 becomes an empty line or the title line).

### Error Handling

- If any toctree entry references a non-existent file, `sphinx-build -W` will fail. Ensure all paths are correct relative to `docs/source/`.

## Acceptance Criteria

- [ ] Given `docs/source/index.rst`, when reading the file, then it contains a toctree with `:caption: Guias` that includes entries `guides/architecture`, `guides/performance`, and `guides/migration-v1.9`
- [ ] Given `docs/source/index.rst`, when reading the file, then it contains a toctree with `:caption: Recursos` that includes the entry `guides/faq`
- [ ] Given `docs/source/index.rst`, when reading the file, then it contains `:caption: Primeiros Passos` instead of `:caption: Getting Started`
- [ ] Given `docs/source/index.rst`, when reading the file, then it contains `:caption: Instalacao` instead of `:caption: Install`
- [ ] Given `docs/source/index.rst`, when reading the file, then it contains `:caption: Referencia de Modulos` instead of `:caption: Module Reference`
- [ ] Given `docs/source/guides/architecture.rst`, when reading line 1, then it does NOT contain the text `:orphan:`
- [ ] Given `docs/source/guides/faq.rst`, when reading line 1, then it does NOT contain the text `:orphan:`
- [ ] Given `docs/source/guides/migration-v1.9.rst`, when reading line 1, then it does NOT contain the text `:orphan:`
- [ ] Given `docs/source/guides/performance.rst`, when reading line 1, then it does NOT contain the text `:orphan:`
- [ ] Given the command `uv run sphinx-build -W -b html docs/source docs/build/html`, when executed from the repository root, then the build completes with exit code 0 and zero warnings

## Implementation Guide

### Suggested Approach

1. **Edit `docs/source/index.rst`**:
   - Translate the introductory paragraph to pt-BR.
   - Rename section captions: "Install" to "Instalacao", "Getting Started" to "Primeiros Passos", "Module Reference" to "Referencia de Modulos".
   - Add a new toctree block after "Primeiros Passos" with `:caption: Guias` and `:maxdepth: 2`, containing `guides/architecture`, `guides/performance`, `guides/migration-v1.9`.
   - Add a new toctree block after "Referencia de Modulos" with `:caption: Recursos` and `:maxdepth: 2`, containing `guides/faq`.
   - Keep the `:ref:\`genindex\`` at the end.

2. **Remove `:orphan:` from each guide file**:
   - For each of the 4 files, delete line 1 (the `:orphan:` directive). The blank line that follows becomes the new line 1 (before the title).

3. **Run Sphinx build** to verify:
   ```bash
   uv run sphinx-build -W -b html docs/source docs/build/html
   ```

### Key Files to Modify

- `docs/source/index.rst` (MODIFY)
- `docs/source/guides/architecture.rst` (MODIFY -- remove line 1)
- `docs/source/guides/faq.rst` (MODIFY -- remove line 1)
- `docs/source/guides/migration-v1.9.rst` (MODIFY -- remove line 1)
- `docs/source/guides/performance.rst` (MODIFY -- remove line 1)

### Patterns to Follow

- Use `:maxdepth: 2` for new toctree sections (consistent with Module Reference).
- Use `:maxdepth: 3` for Install and Primeiros Passos (consistent with existing).
- Toctree entries use paths relative to `docs/source/` without `.rst` extension (e.g., `guides/architecture` not `guides/architecture.rst`).

### Pitfalls to Avoid

- Do NOT leave `:orphan:` in any file that is now in a toctree -- Sphinx will emit a warning under `-W`.
- Do NOT add `.rst` extension to toctree entries -- Sphinx resolves the extension automatically.
- Do NOT reorder the existing entries within "Primeiros Passos" or "Referencia de Modulos" -- only rename captions and add new sections.
- Do NOT forget to remove the blank line left after deleting `:orphan:` if it creates a double-blank-line before the title (RST titles need at most one blank line before them).

## Testing Requirements

### Unit Tests

Not applicable (documentation structure changes).

### Integration Tests

- Run `uv run sphinx-build -W -b html docs/source docs/build/html` and verify exit code 0 with zero warnings.
- Grep each guide file for `:orphan:` to confirm removal.
- Grep `index.rst` for each expected caption string.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-007-create-architecture-overview.md, ticket-008-create-faq-page.md, ticket-009-create-migration-guide.md, ticket-010-create-performance-tips-page.md, ticket-011-update-contributing-rst.md (all pages must exist before adding toctree entries)
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: High
