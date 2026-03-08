# ticket-012 Create root-level CONTRIBUTING.md

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Create a root-level `CONTRIBUTING.md` file in pt-BR that GitHub renders automatically when users navigate to the repository's contributing guidelines. The file should provide a concise overview of how to contribute (report bugs, submit PRs, development setup) and link to the full contributing guide in the Sphinx documentation for detailed instructions.

## Anticipated Scope

- **Files likely to be modified**: `CONTRIBUTING.md` (CREATE at repository root)
- **Key decisions needed**: Whether CONTRIBUTING.md duplicates content from contributing.rst or simply redirects, exact URL for the Sphinx docs contributing page after deployment
- **Open questions**: Should CONTRIBUTING.md include a code of conduct reference? Should it mention the pre-commit hooks and CI checks?

## Dependencies

- **Blocked By**: ticket-011-update-contributing-rst.md (the Sphinx contributing page must be finalized first so CONTRIBUTING.md can link to it)
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: Low (will be re-estimated during refinement)
