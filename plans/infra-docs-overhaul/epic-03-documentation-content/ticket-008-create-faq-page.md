# ticket-008 Create FAQ page

## Context

### Background

Users of cfinterface frequently need guidance on choosing between Register, Block, and Section models, handling binary files, using the optional pandas integration, defining custom fields, and troubleshooting parsing errors. Currently there is no FAQ page in the documentation. This ticket creates a "Perguntas Frequentes" page in pt-BR that addresses these common questions with concise answers and code snippets.

### Relation to Epic

Epic 03 creates five documentation content pages. This ticket produces the FAQ, which complements the architecture overview (ticket-007) by providing practical, question-driven guidance rather than conceptual exposition. It does not modify `index.rst` -- that is handled by ticket-013.

### Current State

- `docs/source/guides/` directory will be created by ticket-007 (or this ticket if executed first)
- `docs/source/conf.py` has `language = "pt_BR"` and Furo theme
- The codebase provides three file models: `RegisterFile` (identifier-based line parsing), `BlockFile` (begin/end pattern matching), `SectionFile` (ordered sections)
- pandas is an optional dependency since v1.9.0, installed via `pip install cfinterface[pandas]`
- Custom fields are created by subclassing `Field` and implementing `_textual_read`, `_textual_write`, `_binary_read`, `_binary_write`

## Specification

### Requirements

1. Create `docs/source/guides/faq.rst` in pt-BR containing:
   - Title: "Perguntas Frequentes (FAQ)"
   - Q1: "Quando usar Register, Block ou Section?" -- explain that Register is for files with line-by-line identifier patterns, Block is for files with begin/end delimiters enclosing multi-line data, Section is for files with ordered sequential sections
   - Q2: "Como lidar com arquivos binarios?" -- explain `StorageType.BINARY`, show how to set `STORAGE = StorageType.BINARY` on a file class, mention that Field's `_binary_read`/`_binary_write` methods handle bytes
   - Q3: "Como usar a integracao com pandas?" -- explain the optional dependency, `pip install cfinterface[pandas]`, `_as_df()` method on file classes, lazy import behavior
   - Q4: "Como definir um campo personalizado?" -- show a minimal custom Field subclass implementing `_textual_read`, `_textual_write`, `_binary_read`, `_binary_write`
   - Q5: "Como resolver erros comuns de parsing?" -- cover: value is None (field could not parse), encoding issues (use ENCODING class attribute), register not found (check IDENTIFIER and IDENTIFIER_DIGITS)
   - Q6: "Como usar o TabularParser?" -- brief explanation with reference to the gallery example and API docs
   - Q7: "Como funciona o versionamento de arquivos?" -- explain VERSIONS dict, SchemaVersion, resolve_version(), with a brief example

### Inputs/Props

- Source code for accurate class/method names and signatures
- Gallery examples in `docs/source/examples/` for cross-references

### Outputs/Behavior

- A single RST file at `docs/source/guides/faq.rst` that renders without Sphinx warnings
- Each question uses a RST section header (e.g., `Quando usar Register, Block ou Section?` with `-` underline)
- Code examples use `.. code-block:: python`
- All prose in pt-BR

### Error Handling

- N/A (documentation page)

## Acceptance Criteria

- [ ] Given the ticket is implemented, when checking `docs/source/guides/faq.rst`, then the file exists and contains the title "Perguntas Frequentes (FAQ)"
- [ ] Given `docs/source/guides/faq.rst` exists, when counting RST section headers (lines followed by a line of `-` or `~` characters), then there are at least 7 question sections
- [ ] Given `docs/source/guides/faq.rst` exists, when searching for `.. code-block:: python`, then at least 4 code blocks are present (Q2 binary example, Q3 pandas example, Q4 custom field example, Q6 tabular example)
- [ ] Given `docs/source/guides/faq.rst` exists, when running `sphinx-build -W -b html docs/source docs/build/html`, then the build completes with exit code 0

## Implementation Guide

### Suggested Approach

1. Create `docs/source/guides/` directory if it does not exist (it may already exist from ticket-007)
2. Create `docs/source/guides/faq.rst` with the title
3. Write each Q&A as a section. For each question:
   - Use the question text as the section header
   - Write a concise answer (3-8 lines of prose)
   - Include a code snippet where applicable
4. For Q1, provide a decision table or bullet list comparing Register vs Block vs Section
5. For Q4 (custom field), show a minimal subclass of `Field`:

   ```python
   from cfinterface.components.field import Field

   class MyCustomField(Field):
       def _textual_read(self, line: str):
           return line[self._starting_position:self._ending_position].strip()
       def _textual_write(self, line: str) -> str:
           # ...
       def _binary_read(self, line: bytes):
           # ...
       def _binary_write(self, line: bytes) -> bytes:
           # ...
   ```

6. Use `:class:` and `:func:` cross-references to link to API docs
7. Do NOT modify `index.rst`

### Key Files to Modify

- `docs/source/guides/faq.rst` (CREATE)

### Patterns to Follow

- RST section hierarchy: `=` for title, `-` for question headers
- `.. code-block:: python` for examples
- `:class:` / `:func:` roles for API references
- All prose in pt-BR

### Pitfalls to Avoid

- Do NOT add toctree entry to `index.rst` -- ticket-013 handles that
- Do NOT duplicate full API documentation -- keep answers concise and link to reference docs
- Do NOT use pandas in examples without noting it is optional (`pip install cfinterface[pandas]`)
- Do NOT show deprecated patterns (bare string `"TEXT"` for storage) -- always use `StorageType.TEXT`

## Testing Requirements

### Unit Tests

- N/A (documentation content)

### Integration Tests

- Run `sphinx-build -W -b html docs/source docs/build/html` and verify exit code 0
- Verify `docs/build/html/guides/faq.html` exists

### E2E Tests

- N/A

## Dependencies

- **Blocked By**: ticket-006-update-conf-language-intersphinx.md
- **Blocks**: ticket-013-restructure-index-rst.md

## Effort Estimate

**Points**: 2
**Confidence**: High
