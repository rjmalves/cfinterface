# ticket-011 Update contributing.rst content and fix repository URL

## Context

### Background

The current `docs/source/getting_started/contributing.rst` has several issues: the git clone URL points to `inewave` instead of `cfinterface`, development setup instructions use `pip install .[dev]` instead of `uv`, there is no mention of pre-commit hooks (added in ticket-001), and the testing section does not mention pytest markers or benchmark tests. The content is in English but should be in pt-BR to match the `language = "pt_BR"` setting in conf.py.

### Relation to Epic

Epic 03 creates five documentation content pages. This ticket rewrites the existing contributing guide with correct information. It is blocked by ticket-001 (pre-commit config must exist to be documented). It blocks ticket-012 (root CONTRIBUTING.md) which will reference this Sphinx page.

### Current State

- `docs/source/getting_started/contributing.rst` exists with 50 lines of English content
- The file has an incorrect clone URL: `https://github.com/rjmalves/inewave.git` (should be `cfinterface`)
- Development setup uses `pip install .[dev]` (should use `uv`)
- No mention of pre-commit hooks
- `.pre-commit-config.yaml` exists at repository root with ruff (lint + format) and mypy hooks
- `pyproject.toml` has `[project.optional-dependencies]` with `dev` extra containing all dev dependencies
- The project uses `uv` for dependency management (as established in CI workflows from epic-01)

## Specification

### Requirements

1. Rewrite `docs/source/getting_started/contributing.rst` entirely in pt-BR with the following content:
   - Title: "Contribuindo"
   - Introduction paragraph explaining how to report bugs (GitHub issues) and submit pull requests, with correct repository URL `https://github.com/rjmalves/cfinterface`
   - Section "Configuracao do Ambiente de Desenvolvimento":
     - Clone command with correct URL: `git clone https://github.com/rjmalves/cfinterface.git`
     - `cd cfinterface`
     - Install with uv: `uv sync --extra dev`
     - Install pre-commit hooks: `uv run pre-commit install`
   - Section "Hooks de Pre-commit":
     - Explain that the project uses pre-commit with 3 hooks: `ruff` (lint with auto-fix), `ruff-format` (formatting), `mypy` (type checking on `cfinterface/` only)
     - Show how to run manually: `uv run pre-commit run --all-files`
   - Section "Convencoes de Codigo":
     - Explain ruff for linting and formatting, mypy for static typing
     - Show commands: `uv run ruff check ./cfinterface`, `uv run ruff format --check ./cfinterface`, `uv run mypy ./cfinterface`
   - Section "Testes":
     - Explain pytest as the testing framework
     - Show command: `uv run pytest ./tests`
     - Mention pytest-benchmark for performance tests: `uv run pytest ./tests --benchmark-only`
     - Mention pytest-cov for coverage: `uv run pytest ./tests --cov=cfinterface`
   - Section "Documentacao":
     - Explain that docs are built with Sphinx and Furo theme
     - Show command: `uv run sphinx-build -W -b html docs/source docs/build/html`
     - Note that built docs should NOT be committed -- GitHub Actions handles deployment
   - Remove the existing `.. warning::` about not committing built docs (rewrite it as a `.. note::` in the Documentacao section)

### Inputs/Props

- `.pre-commit-config.yaml` for hook names and configuration
- `pyproject.toml` for dev dependency list and tool configuration

### Outputs/Behavior

- The file `docs/source/getting_started/contributing.rst` is rewritten in-place with pt-BR content
- All commands use `uv run` prefix for tool invocation
- The incorrect `inewave` URL is replaced with `cfinterface`

### Error Handling

- N/A (documentation page)

## Acceptance Criteria

- [ ] Given the ticket is implemented, when checking `docs/source/getting_started/contributing.rst`, then the file contains the title "Contribuindo" and does NOT contain the string "inewave"
- [ ] Given the rewritten file exists, when searching for `uv sync --extra dev`, then exactly 1 match is found
- [ ] Given the rewritten file exists, when searching for `pre-commit`, then at least 3 matches are found (install command, run command, section header or explanation)
- [ ] Given the rewritten file exists, when searching for `uv run pytest`, then at least 1 match is found
- [ ] Given the rewritten file exists, when running `sphinx-build -W -b html docs/source docs/build/html`, then the build completes with exit code 0

## Implementation Guide

### Suggested Approach

1. Read the current `docs/source/getting_started/contributing.rst` to understand the existing structure
2. Rewrite the file entirely with the new pt-BR content
3. Structure the RST with `=` for title and `-` for sections
4. For the setup section, use `::` or `.. code-block:: bash` for shell commands
5. For the pre-commit section, reference the actual hooks from `.pre-commit-config.yaml`: `ruff` (v0.9.10), `ruff-format`, `mypy` (v1.19.1)
6. Keep the `.. note::` about not committing built docs in the Documentacao section
7. Use correct RST link syntax for GitHub URLs: `` `issues <URL>`_ `` and `` `pull requests <URL>`_ ``

### Key Files to Modify

- `docs/source/getting_started/contributing.rst` (REWRITE)

### Patterns to Follow

- RST section hierarchy: `=` for title, `-` for sections (consistent with existing `tutorial.rst`)
- `.. code-block:: bash` for shell commands
- `.. note::` for important callouts
- `:class:` / `:func:` roles only if referencing cfinterface API (unlikely in this page)
- All prose in pt-BR

### Pitfalls to Avoid

- Do NOT change the file location -- it must remain at `docs/source/getting_started/contributing.rst` to preserve the existing toctree reference in `index.rst`
- Do NOT add new toctree entries -- the file is already referenced in `index.rst` under "Getting Started"
- Do NOT use `pip` in any command -- all commands should use `uv` or `uv run`
- Do NOT document the CI workflows in detail -- that is out of scope; just mention that CI runs the same checks
- Do NOT reference ticket-012 (CONTRIBUTING.md) -- it does not exist yet

## Testing Requirements

### Unit Tests

- N/A (documentation content)

### Integration Tests

- Run `sphinx-build -W -b html docs/source docs/build/html` and verify exit code 0
- Verify `docs/build/html/getting_started/contributing.html` exists and is non-empty

### E2E Tests

- N/A

## Dependencies

- **Blocked By**: ticket-001-add-pre-commit-configuration.md (must reference the actual pre-commit config)
- **Blocks**: ticket-012-create-root-contributing-md.md

## Effort Estimate

**Points**: 1
**Confidence**: High
