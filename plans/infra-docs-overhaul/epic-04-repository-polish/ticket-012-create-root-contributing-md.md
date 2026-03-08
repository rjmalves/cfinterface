# ticket-012 Create root-level CONTRIBUTING.md

## Context

### Background

GitHub automatically renders a `CONTRIBUTING.md` file at the repository root when users navigate to the "Contributing" tab or open new issues/PRs. Currently, cfinterface has detailed contributing documentation only inside the Sphinx docs at `docs/source/getting_started/contributing.rst` (rewritten in ticket-011). A root-level `CONTRIBUTING.md` is needed so that GitHub surfaces contributing guidance without requiring users to visit the deployed Sphinx site.

### Relation to Epic

This is the first ticket in Epic 04 (Repository Polish). It creates a lightweight root-level file that complements the comprehensive Sphinx contributing page, improving GitHub discoverability.

### Current State

- `CONTRIBUTING.md` does not exist at the repository root.
- `docs/source/getting_started/contributing.rst` contains the full contributing guide in pt-BR, covering: bug reporting, dev environment setup with `uv`, pre-commit hooks (ruff, ruff-format, mypy), code conventions, tests (pytest, pytest-benchmark, pytest-cov), and documentation build (Sphinx + Furo).
- The deployed docs URL pattern is `https://rjmalves.github.io/cfinterface/`.

## Specification

### Requirements

1. Create `CONTRIBUTING.md` at the repository root (`/home/rogerio/git/cfinterface/CONTRIBUTING.md`).
2. Write content in pt-BR (matching the project convention established in epics 02-03).
3. Include a concise summary (not a full duplication) covering:
   - How to report bugs (link to GitHub Issues)
   - How to submit pull requests (link to GitHub PRs)
   - Quick dev setup commands (`git clone`, `uv sync --extra dev`, `uv run pre-commit install`)
   - Link to the full Sphinx contributing page for detailed instructions
4. Do NOT duplicate the full content of `contributing.rst` -- keep CONTRIBUTING.md under 60 lines.

### Inputs/Props

- Repository URL: `https://github.com/rjmalves/cfinterface`
- Sphinx docs contributing page relative path: `getting_started/contributing.html`

### Outputs/Behavior

A single Markdown file at the repository root that GitHub renders in the "Contributing" UI surface.

### Error Handling

Not applicable (static file creation).

## Acceptance Criteria

- [ ] Given the repository root directory, when listing files, then `CONTRIBUTING.md` exists at `/home/rogerio/git/cfinterface/CONTRIBUTING.md`
- [ ] Given the content of `CONTRIBUTING.md`, when reading the file, then it is written in pt-BR prose (Portuguese section headings and body text)
- [ ] Given the content of `CONTRIBUTING.md`, when searching for links, then it contains a link to `https://github.com/rjmalves/cfinterface/issues` for bug reporting
- [ ] Given the content of `CONTRIBUTING.md`, when searching for links, then it contains a link to `https://github.com/rjmalves/cfinterface/pulls` for pull requests
- [ ] Given the content of `CONTRIBUTING.md`, when reading the dev setup section, then it includes the commands `git clone`, `uv sync --extra dev`, and `uv run pre-commit install`
- [ ] Given the content of `CONTRIBUTING.md`, when counting lines with `wc -l`, then the file has fewer than 60 lines

## Implementation Guide

### Suggested Approach

1. Create `CONTRIBUTING.md` at the repository root.
2. Structure the file with the following sections in pt-BR:
   - Title: `# Contribuindo`
   - Brief intro paragraph explaining the file links to the full docs
   - `## Reportando Bugs` -- 2-3 sentences with link to GitHub Issues
   - `## Enviando Pull Requests` -- 2-3 sentences with link to GitHub PRs
   - `## Configuracao Rapida` -- code block with the 3 setup commands
   - `## Documentacao Completa` -- link to the full Sphinx contributing page
3. Follow the pt-BR convention: prose in Portuguese, code/commands in English, class/function names in English.

### Key Files to Modify

- `CONTRIBUTING.md` (CREATE)

### Patterns to Follow

- Match the tone and style of `docs/source/getting_started/contributing.rst` (ticket-011).
- Use standard GitHub Markdown (not reStructuredText).

### Pitfalls to Avoid

- Do NOT duplicate the full contributing.rst content -- CONTRIBUTING.md is a summary with a redirect link.
- Do NOT use reStructuredText syntax in the Markdown file.
- Do NOT hardcode a specific Sphinx docs URL that includes a version number -- use the base URL `https://rjmalves.github.io/cfinterface/`.

## Testing Requirements

### Unit Tests

Not applicable (static documentation file).

### Integration Tests

- Run `test -f CONTRIBUTING.md` to verify the file exists.
- Run `wc -l CONTRIBUTING.md` to verify line count is under 60.

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-011-update-contributing-rst.md (the Sphinx contributing page must be finalized so CONTRIBUTING.md can reference it accurately)
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: High
