# ticket-020 Final Release Preparation Review

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Perform a final consistency review before the v1.9.0 release: verify version number consistency across `cfinterface/__init__.py`, `pyproject.toml`, and `CHANGELOG.md`; confirm all classifiers are correct; verify py.typed is included in the built wheel; confirm all CI workflows pass; and check that documentation links are functional.

## Anticipated Scope

- **Files likely to be modified**: Potentially `cfinterface/__init__.py` (if version needs update), `pyproject.toml` (if metadata needs correction), `CHANGELOG.md` (if release date needs to be set)
- **Key decisions needed**: Whether to bump version from 1.9.0 or keep it (depends on whether it was already released), what date to set in CHANGELOG
- **Open questions**: Is v1.9.0 already released or is this pre-release? Should the review include building and inspecting the wheel?

## Dependencies

- **Blocked By**: ticket-019-create-changelog (CHANGELOG must exist for version consistency check)
- **Blocks**: None (final ticket in the plan)

## Effort Estimate

**Points**: 1
**Confidence**: Low (will be re-estimated during refinement)
