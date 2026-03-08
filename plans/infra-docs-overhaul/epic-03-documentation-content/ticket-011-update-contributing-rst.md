# ticket-011 Update contributing.rst content and fix repository URL

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Rewrite `docs/source/getting_started/contributing.rst` in pt-BR with correct information: fix the clone URL (currently points to `inewave` instead of `cfinterface`), update development setup instructions to use `uv` instead of `pip`, document the pre-commit hooks (from ticket-001), and update the testing section with current pytest markers and benchmark information.

## Anticipated Scope

- **Files likely to be modified**: `docs/source/getting_started/contributing.rst` (REWRITE)
- **Key decisions needed**: Whether to keep the contributing guide in the Sphinx docs or redirect entirely to root CONTRIBUTING.md (ticket-012), level of detail for pre-commit hook documentation
- **Open questions**: Should the contributing guide include CI workflow documentation (what each workflow does)? Should it document the release process?

## Dependencies

- **Blocked By**: ticket-001-add-pre-commit-configuration.md (must reference the actual pre-commit config that was created)
- **Blocks**: ticket-012-create-root-contributing-md.md

## Effort Estimate

**Points**: 1
**Confidence**: Low (will be re-estimated during refinement)
