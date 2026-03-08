# ticket-005 Add sphinx-gallery examples for BlockFile and SectionFile

## Context

### Background

The cfinterface examples gallery currently has three examples: `plot_register_file.py` (RegisterFile), `plot_tabular_parsing.py` (TabularParser), and `plot_versioned_file.py` (versioning). The two other major file types -- `BlockFile` and `SectionFile` -- have no gallery examples, leaving users without practical demonstrations of these APIs.

### Relation to Epic

This is the second ticket in Epic 02 (Sphinx Modernization). It expands the examples gallery to provide comprehensive coverage of all major cfinterface file types.

### Current State

Directory `/home/rogerio/git/cfinterface/examples/` contains:

- `README.rst` -- gallery introduction
- `__init__.py` -- package marker
- `plot_register_file.py` -- RegisterFile example
- `plot_tabular_parsing.py` -- TabularParser example
- `plot_versioned_file.py` -- versioned file example

The sphinx-gallery configuration in `conf.py` points `examples_dirs` to `../../examples` and `gallery_dirs` to `examples`.

## Specification

### Requirements

1. Create `plot_block_file.py` in `/home/rogerio/git/cfinterface/examples/` demonstrating a `BlockFile` with `Block` subclasses using beginning/ending patterns
2. Create `plot_section_file.py` in `/home/rogerio/git/cfinterface/examples/` demonstrating a `SectionFile` with `Section` subclasses for ordered file divisions
3. Both examples must follow sphinx-gallery script format (module docstring as title, `# %%` cell separators, matplotlib or text-only output)
4. Both examples must be self-contained (create sample data in-memory, no external file dependencies)
5. Example content and comments should be in pt-BR

### Inputs/Props

- Existing example scripts in `/home/rogerio/git/cfinterface/examples/` as reference for style
- cfinterface API: `Block`, `BlockFile`, `BlockData`, `Section`, `SectionFile`, `SectionData`

### Outputs/Behavior

- Two new `.py` files appear in the examples gallery when docs are built
- Each example renders as a gallery page with code cells, explanatory text, and output
- `sphinx-build -W` continues to pass

### Error Handling

- If the example scripts have import errors or runtime exceptions, the sphinx-gallery build will fail and report the error

## Acceptance Criteria

- [ ] Given the examples directory, when its contents are listed, then `plot_block_file.py` and `plot_section_file.py` are present
- [ ] Given `plot_block_file.py`, when it is executed with `python examples/plot_block_file.py`, then it runs without errors and produces output to stdout
- [ ] Given `plot_section_file.py`, when it is executed with `python examples/plot_section_file.py`, then it runs without errors and produces output to stdout
- [ ] Given a clean install, when `uv run python -m sphinx -M html docs/source docs/build -W` is executed, then the gallery page shows 5 examples (3 existing + 2 new) and the exit code is 0
- [ ] Given `plot_block_file.py`, when its module docstring is read, then it is written in pt-BR

## Implementation Guide

### Suggested Approach

1. Read existing examples (`plot_register_file.py`, `plot_tabular_parsing.py`) to understand the sphinx-gallery format used in this project
2. Create `plot_block_file.py`:
   - Title: "Lendo arquivos com BlockFile"
   - Define a simple `Block` subclass with `BEGIN_PATTERN` and `END_PATTERN`
   - Create a `BlockFile` subclass with `BLOCKS = [MyBlock]`
   - Write sample data to a `StringIO`, read it, and print the parsed blocks
3. Create `plot_section_file.py`:
   - Title: "Lendo arquivos com SectionFile"
   - Define a simple `Section` subclass
   - Create a `SectionFile` subclass with `SECTIONS = [MySection]`
   - Write sample data to a `StringIO`, read it, and print the parsed sections
4. Run `uv run python -m sphinx -M html docs/source docs/build -W` to verify

### Key Files to Modify

- `/home/rogerio/git/cfinterface/examples/plot_block_file.py` (CREATE)
- `/home/rogerio/git/cfinterface/examples/plot_section_file.py` (CREATE)

### Patterns to Follow

Follow the existing example structure from `plot_register_file.py`:

- Module docstring as the gallery title
- `# %%` cell separators between sections
- Print statements for output (sphinx-gallery captures stdout)
- Use `StringIO` or `tempfile` for sample data instead of external files

### Pitfalls to Avoid

- Do NOT use `matplotlib.pyplot` unless the example genuinely needs a plot -- text output is preferred for data parsing examples
- Do NOT import from test fixtures -- examples must be fully self-contained
- Do NOT forget the `# %%` cell separators -- without them, sphinx-gallery treats the entire script as one cell
- File names MUST start with `plot_` for sphinx-gallery to pick them up (this is the default `filename_pattern`)

## Testing Requirements

### Unit Tests

Not applicable.

### Integration Tests

- Run each example script standalone: `python examples/plot_block_file.py` and `python examples/plot_section_file.py`
- Run `uv run python -m sphinx -M html docs/source docs/build -W` and verify the gallery renders correctly

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: ticket-004-migrate-sphinx-theme-to-furo.md (examples should be built with the new theme)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
