# ticket-004 Migrate Sphinx theme from RTD to Furo

## Context

### Background

The cfinterface documentation uses `sphinx-rtd-theme` which lacks dark mode support, has less responsive mobile rendering, and receives less active maintenance compared to Furo. The sibling project sintetizador-newave has already migrated to Furo, establishing it as the standard theme for the ecosystem.

### Relation to Epic

This is the first ticket in Epic 02 (Sphinx Modernization). The theme migration must happen before other Sphinx configuration changes to ensure a clean baseline.

### Current State

File `/home/rogerio/git/cfinterface/docs/source/conf.py`:

- Line 49: `"sphinx_rtd_theme"` is listed in `extensions`
- Line 88: `html_theme = "sphinx_rtd_theme"`
- Lines 89-97: `html_theme_options` dict with RTD-specific keys (`logo_only`, `collapse_navigation`, `sticky_navigation`, `navigation_depth`, `includehidden`, `titles_only`)

File `/home/rogerio/git/cfinterface/pyproject.toml`:

- Line 50: `"sphinx-rtd-theme"` in dev dependencies

## Specification

### Requirements

1. Replace `sphinx-rtd-theme` with `furo` in `pyproject.toml` dev dependencies
2. Remove `"sphinx_rtd_theme"` from `extensions` list in `conf.py` (Furo is not loaded as an extension)
3. Change `html_theme = "sphinx_rtd_theme"` to `html_theme = "furo"` in `conf.py`
4. Replace `html_theme_options` with Furo-compatible options (light/dark mode toggle, sidebar navigation)
5. Preserve `html_logo` and `html_static_path` settings
6. Verify `sphinx-build -W` passes with no warnings

### Inputs/Props

- Current `conf.py` at `/home/rogerio/git/cfinterface/docs/source/conf.py`
- Current `pyproject.toml` at `/home/rogerio/git/cfinterface/pyproject.toml`

### Outputs/Behavior

- Documentation builds with Furo theme
- Dark mode toggle is available in the rendered documentation
- Logo renders correctly in the sidebar
- All existing documentation pages render without warnings

### Error Handling

- If `sphinx-build -W` produces warnings, they must be resolved before the ticket is complete

## Acceptance Criteria

- [ ] Given `pyproject.toml`, when the dev dependencies list is read, then it contains `"furo"` and does not contain `"sphinx-rtd-theme"`
- [ ] Given `docs/source/conf.py`, when the `extensions` list is read, then it does not contain `"sphinx_rtd_theme"`
- [ ] Given `docs/source/conf.py`, when `html_theme` is read, then its value is `"furo"`
- [ ] Given `docs/source/conf.py`, when `html_theme_options` is read, then it does not contain RTD-specific keys (`logo_only`, `collapse_navigation`, `sticky_navigation`, `navigation_depth`, `includehidden`, `titles_only`)
- [ ] Given a clean install with `uv sync --all-extras --dev`, when `uv run python -m sphinx -M html docs/source docs/build -W` is executed, then the exit code is 0

## Implementation Guide

### Suggested Approach

1. In `pyproject.toml`, replace `"sphinx-rtd-theme"` with `"furo"` in the dev dependencies list
2. In `conf.py`, remove `"sphinx_rtd_theme"` from the `extensions` list
3. In `conf.py`, change `html_theme = "sphinx_rtd_theme"` to `html_theme = "furo"`
4. Replace the `html_theme_options` dict with Furo-compatible options:
   ```python
   html_theme_options = {
       "light_css_variables": {
           "color-brand-primary": "#2980B9",
           "color-brand-content": "#2980B9",
       },
       "navigation_with_keys": True,
   }
   ```
5. Keep `html_logo`, `html_static_path`, and all other non-theme settings unchanged
6. Run `uv sync --all-extras --dev && uv run python -m sphinx -M html docs/source docs/build -W`

### Key Files to Modify

- `/home/rogerio/git/cfinterface/docs/source/conf.py` (MODIFY: theme settings)
- `/home/rogerio/git/cfinterface/pyproject.toml` (MODIFY: swap dependency)

### Patterns to Follow

Furo does not use the `extensions` mechanism -- it is set only via `html_theme`. This is different from RTD theme which required both.

### Pitfalls to Avoid

- Do NOT remove the `sphinx_gallery` extension or `numpydoc` -- only remove `sphinx_rtd_theme` from extensions
- Do NOT change `html_logo` path -- the SVG logo should work with Furo
- Do NOT add `sphinx_rtd_theme` to `exclude_patterns` -- just remove it from extensions
- Furo's `html_theme_options` keys are entirely different from RTD's -- do not carry over RTD keys

## Testing Requirements

### Unit Tests

Not applicable.

### Integration Tests

- Run `uv run python -m sphinx -M html docs/source docs/build -W` and verify exit code 0
- Open `docs/build/html/index.html` in a browser and verify dark mode toggle is present

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None
- **Blocks**: ticket-005-add-sphinx-gallery-examples.md, ticket-006-update-conf-language-intersphinx.md

## Effort Estimate

**Points**: 2
**Confidence**: High
