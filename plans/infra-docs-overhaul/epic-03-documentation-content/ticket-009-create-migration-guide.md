# ticket-009 Create v1.8-to-v1.9 migration guide

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Create a migration guide RST page in pt-BR documenting all breaking changes and new features between cfinterface v1.8.x and v1.9.0. Cover the pandas-to-optional migration, StorageType enum adoption, deprecated set_version() replacement, new TabularParser API, and read_many() batch API. Include before/after code examples for each migration step so downstream users can update their code systematically.

## Anticipated Scope

- **Files likely to be modified**: `docs/source/guides/migration-v1.9.rst` (CREATE), `docs/source/index.rst` (ADD toctree entry)
- **Key decisions needed**: Directory structure for guide pages, whether to include migration steps for internal API changes (adapter layer) or only public API
- **Open questions**: Should the migration guide reference the CHANGELOG or duplicate the information in a more tutorial-like format? Should it include automated migration scripts or just manual instructions?

## Dependencies

- **Blocked By**: ticket-006-update-conf-language-intersphinx.md
- **Blocks**: ticket-013-restructure-index-rst.md

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
