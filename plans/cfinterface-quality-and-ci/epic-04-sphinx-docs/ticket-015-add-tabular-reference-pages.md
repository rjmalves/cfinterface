# ticket-015 Create Sphinx Reference Pages for TabularParser

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Create Sphinx reference documentation pages for `TabularParser`, `TabularSection`, and `ColumnDef` — the tabular parsing subsystem introduced in the architecture overhaul. These are the most critical documentation gaps: the tabular parser is a major new feature with no reference pages. The pages should use `autodoc` with the existing numpydoc-style docstrings and be integrated into the documentation toctree.

## Anticipated Scope

- **Files likely to be modified**: `docs/source/reference/tabular/index.rst` (create directory and index), `docs/source/reference/tabular/files/tabularparser.rst` (create), `docs/source/reference/tabular/files/tabularsection.rst` (create), `docs/source/reference/tabular/files/columndef.rst` (create), `docs/source/index.rst` (add tabular to toctree)
- **Key decisions needed**: Whether to create a new top-level "Tabular" reference section or nest under "Sections", what level of detail to include beyond autodoc (usage examples, class diagrams)
- **Open questions**: Should TabularSection be documented alongside Section or in its own section? Does the sphinx-build -W pass after adding these pages (depends on docstring completeness)?

## Dependencies

- **Blocked By**: ticket-004-fix-mypy-strict-errors (type annotations may affect autodoc output)
- **Blocks**: ticket-018-fix-docstrings-and-index (index.rst updates)

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
