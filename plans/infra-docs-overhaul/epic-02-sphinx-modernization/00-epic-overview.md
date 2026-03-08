# Epic 02: Sphinx Modernization

## Goals

Migrate the Sphinx documentation from the RTD theme to Furo, set the documentation language to pt-BR, and expand the examples gallery with new use cases.

## Scope

1. Replace `sphinx-rtd-theme` with `furo` in conf.py and pyproject.toml
2. Update conf.py language, theme options, and remove RTD-specific configuration
3. Add new sphinx-gallery examples covering BlockFile and SectionFile patterns

## Success Criteria

- `sphinx-build -W` passes with Furo theme
- Documentation renders correctly with dark mode toggle
- Language is set to `pt-BR` in conf.py
- At least 2 new example scripts in the gallery
- RTD theme fully removed from dependencies and configuration

## Tickets

| ID         | Title                                                     | Effort |
| ---------- | --------------------------------------------------------- | ------ |
| ticket-004 | Migrate Sphinx theme from RTD to Furo                     | 2 pts  |
| ticket-005 | Add sphinx-gallery examples for BlockFile and SectionFile | 2 pts  |
| ticket-006 | Update conf.py language and intersphinx settings          | 1 pt   |
