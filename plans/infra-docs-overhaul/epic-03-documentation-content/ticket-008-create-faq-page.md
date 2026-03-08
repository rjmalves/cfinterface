# ticket-008 Create FAQ page

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Create a FAQ (Perguntas Frequentes) RST page in pt-BR addressing common questions about cfinterface usage: when to use Register vs Block vs Section, how to handle binary files, how to use optional pandas integration, how to define custom fields, and how to troubleshoot common parsing errors. This reduces support burden and helps users self-serve.

## Anticipated Scope

- **Files likely to be modified**: `docs/source/guides/faq.rst` (CREATE), `docs/source/index.rst` (ADD toctree entry)
- **Key decisions needed**: Directory structure for guide pages (same decision as ticket-007), which questions to prioritize based on actual user issues
- **Open questions**: Are there GitHub issues or discussions that reveal the most common user questions? Should the FAQ link to specific API reference pages?

## Dependencies

- **Blocked By**: ticket-006-update-conf-language-intersphinx.md
- **Blocks**: ticket-013-restructure-index-rst.md

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
