# ticket-010 Create performance tips page

## Context

### Background

cfinterface v1.9.0 includes several performance optimizations: regex pattern caching in the adapter layer, FloatField write optimization from O(n) trial loop to at most 3 format attempts, migration from linked-list to array-backed data containers with O(1) `len()`, `read_many()` batch API for reading multiple files, and TabularParser column selection for large tabular files. Users benefit from understanding these optimizations and how to leverage them in their own code.

### Relation to Epic

Epic 03 creates five documentation content pages. This ticket produces the performance tips page, which helps users write efficient code when using cfinterface. It complements the architecture overview (ticket-007) by focusing on runtime behavior rather than design structure.

### Current State

- `docs/source/guides/` directory will be created by ticket-007 (or this ticket if executed first)
- `docs/source/conf.py` has `language = "pt_BR"` and Furo theme
- Key performance-relevant code locations:
  - Regex caching: `cfinterface/adapters/` layer uses `_pattern_cache` dict to cache compiled regex patterns
  - FloatField optimization: `cfinterface/components/floatfield.py` `_textual_write()` uses at most 3 format attempts instead of O(decimal_digits) trial loop
  - Array containers: `cfinterface/data/registerdata.py`, `blockdata.py`, `sectiondata.py` use `list` instead of linked lists
  - `read_many()`: class method on `RegisterFile`, `BlockFile`, `SectionFile` for batch reading
  - TabularParser: `cfinterface/components/tabular.py` with `columns` parameter for selective parsing

## Specification

### Requirements

1. Create `docs/source/guides/performance.rst` in pt-BR containing:
   - Title: "Dicas de Performance"
   - Introduction paragraph explaining that cfinterface v1.9.0 includes internal optimizations and that users can further improve performance through usage patterns
   - Section "Cache de Regex nos Adaptadores" explaining that regex patterns in the adapter layer are compiled once and cached, so users do not need to manually cache patterns; mention that this is automatic and transparent
   - Section "Otimizacao do FloatField" explaining the O(1) write optimization and advising users to use appropriate `decimal_digits` and `size` parameters to minimize formatting overhead
   - Section "Containers Baseados em Array" explaining that RegisterData/BlockData/SectionData now use array-backed lists with O(1) `len()` and efficient iteration, replacing the previous linked-list implementation
   - Section "Leitura em Lote com read_many()" showing how to use `read_many()` to read multiple files in a single call instead of looping with individual `read()` calls, with a before/after code example
   - Section "Selecao de Colunas no TabularParser" explaining how to define only the columns needed via `ColumnDef` to avoid parsing unnecessary data in large tabular files
   - Section "Dicas Gerais" with practical tips: reuse file class instances for multiple reads, prefer `StorageType.TEXT` enum over strings, use `ENCODING` as a single string (not list) when the encoding is known

### Inputs/Props

- Source code for accurate class/method names
- CHANGELOG.md for v1.9.0 optimization descriptions

### Outputs/Behavior

- A single RST file at `docs/source/guides/performance.rst` that renders without Sphinx warnings
- Code examples use `.. code-block:: python`
- All prose in pt-BR
- Qualitative performance comparisons (e.g., "O(1) ao inves de O(n)") rather than benchmark numbers

### Error Handling

- N/A (documentation page)

## Acceptance Criteria

- [ ] Given the ticket is implemented, when checking `docs/source/guides/performance.rst`, then the file exists and contains the title "Dicas de Performance"
- [ ] Given `docs/source/guides/performance.rst` exists, when searching for section headers, then the file contains at least these 6 sections: "Cache de Regex nos Adaptadores", "Otimizacao do FloatField", "Containers Baseados em Array", "Leitura em Lote com read_many()", "Selecao de Colunas no TabularParser", "Dicas Gerais"
- [ ] Given `docs/source/guides/performance.rst` exists, when searching for `.. code-block:: python`, then at least 2 code blocks are present (read_many before/after, TabularParser column selection)
- [ ] Given `docs/source/guides/performance.rst` exists, when running `sphinx-build -W -b html docs/source docs/build/html`, then the build completes with exit code 0

## Implementation Guide

### Suggested Approach

1. Create `docs/source/guides/` directory if it does not exist
2. Create `docs/source/guides/performance.rst` with the title and introduction
3. For each optimization section:
   - Explain what the optimization is and why it matters
   - Show the user-visible impact (e.g., "O(1) `len()` ao inves de O(n) na implementacao anterior")
   - Include a code example where the user can leverage the optimization
4. For the `read_many()` section, show before/after:

   ```python
   # Antes: leitura individual
   files = []
   for path in paths:
       f = MyFile()
       f.read(path)
       files.append(f)

   # Depois: leitura em lote
   files = MyFile.read_many(paths)
   ```

5. For TabularParser column selection, show a `ColumnDef` list with only the needed columns
6. Use `:class:` and `:func:` cross-references for API links
7. Do NOT modify `index.rst`

### Key Files to Modify

- `docs/source/guides/performance.rst` (CREATE)

### Patterns to Follow

- RST section hierarchy: `=` for title, `-` for sections
- `.. code-block:: python` for examples
- Qualitative comparisons, not benchmark numbers
- `:class:` / `:func:` roles for API references
- All prose in pt-BR

### Pitfalls to Avoid

- Do NOT add toctree entry to `index.rst` -- ticket-013 handles that
- Do NOT include actual benchmark numbers from pytest-benchmark -- use qualitative O-notation comparisons
- Do NOT suggest profiling tools or cProfile usage -- keep focused on cfinterface-specific tips
- Do NOT reference the benchmark CI workflow -- that is an internal development tool

## Testing Requirements

### Unit Tests

- N/A (documentation content)

### Integration Tests

- Run `sphinx-build -W -b html docs/source docs/build/html` and verify exit code 0
- Verify `docs/build/html/guides/performance.html` exists

### E2E Tests

- N/A

## Dependencies

- **Blocked By**: ticket-006-update-conf-language-intersphinx.md
- **Blocks**: ticket-013-restructure-index-rst.md

## Effort Estimate

**Points**: 2
**Confidence**: High
