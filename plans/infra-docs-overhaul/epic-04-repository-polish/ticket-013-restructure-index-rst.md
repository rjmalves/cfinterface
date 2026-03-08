# ticket-013 Restructure index.rst with new documentation sections

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Restructure `docs/source/index.rst` to incorporate all new documentation pages created in Epic 03 (architecture, FAQ, migration guide, performance tips) into logical toctree sections. Add a "Guias" (Guides) section for architecture, performance, and migration content, and a "Recursos" (Resources) section for FAQ. Update the introductory text to be in pt-BR.

## Anticipated Scope

- **Files likely to be modified**: `docs/source/index.rst` (MODIFY: add new toctree sections and entries)
- **Key decisions needed**: Exact toctree section names and ordering, whether to keep existing section names in English or translate to pt-BR
- **Open questions**: Should the index page description text be rewritten in pt-BR? Should the "Getting Started" caption become "Primeiros Passos"? How should the new guide pages be ordered relative to existing content?

## Dependencies

- **Blocked By**: ticket-007-create-architecture-overview.md, ticket-008-create-faq-page.md, ticket-009-create-migration-guide.md, ticket-010-create-performance-tips-page.md, ticket-011-update-contributing-rst.md (all new pages must exist before adding toctree entries)
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: Low (will be re-estimated during refinement)
