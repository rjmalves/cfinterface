# ticket-018 Fix Missing Docstrings and Update Documentation Index

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Add the missing docstring to `RegisterFile.read_many()`, fix any other docstring gaps discovered during the Sphinx -W build, and update `docs/source/index.rst` to include all new reference sections (tabular, versioning, storage, adapters) in the toctree. This is the final documentation ticket that ensures `sphinx-build -W` passes cleanly.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/files/registerfile.py` (add read_many docstring), `cfinterface/files/blockfile.py` (check read_many docstring), `cfinterface/files/sectionfile.py` (check read_many docstring), `docs/source/index.rst` (update toctree), potentially other source files with docstring issues surfaced by -W
- **Key decisions needed**: What docstring format to use for read_many (numpydoc Parameters/Returns sections), whether to add docstrings to all adapter methods or only public ones
- **Open questions**: What Sphinx warnings will -W surface beyond missing docstrings? Are there cross-reference issues in existing docstrings?

## Dependencies

- **Blocked By**: ticket-015-add-tabular-reference-pages, ticket-016-add-versioning-reference-page, ticket-017-add-storage-and-adapter-pages (all reference pages must exist before updating index)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
