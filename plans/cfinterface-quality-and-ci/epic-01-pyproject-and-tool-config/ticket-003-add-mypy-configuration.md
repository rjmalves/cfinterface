# ticket-003 Add mypy Configuration to pyproject.toml

## Context

### Background

cfinterface runs mypy with no configuration — no pyproject.toml section, no mypy.ini. This means mypy uses its default settings, which are permissive: untyped functions are silently allowed, `Any` return types are not flagged, and optional types are not strictly checked. The project wants to enable three specific strict flags: `disallow_untyped_defs`, `warn_return_any`, and `strict_optional`. Currently, running mypy with these flags produces 189 errors across 29 files. This ticket adds the mypy configuration section with the strict flags enabled but uses per-module overrides to temporarily suppress errors in files that need annotation work (which ticket-004 will handle).

### Relation to Epic

Third ticket in Epic 1. Adds the mypy configuration that must be in place before ticket-004 can fix the actual type errors. The configuration uses per-module `ignore_errors = true` as a temporary bridge, which ticket-004 then removes file by file.

### Current State

- `/home/rogerio/git/cfinterface/pyproject.toml` has NO `[tool.mypy]` section
- Running `uv run mypy ./cfinterface` with defaults: 33 errors (pre-existing generic issues)
- Running with `--disallow-untyped-defs --warn-return-any --strict-optional`: 189 errors in 29 files
- Error breakdown: 137 `no-untyped-def`, 22 `no-any-return`, 14 `override`, 6 `arg-type`/`misc`/`assignment`, 2 `import-untyped`

## Specification

### Requirements

1. Add `[tool.mypy]` section with:
   - `python_version = "3.10"` (minimum supported version)
   - `disallow_untyped_defs = true`
   - `warn_return_any = true`
   - `strict_optional = true`
   - `warn_unused_configs = true`
   - `show_error_codes = true`
2. Add `[[tool.mypy.overrides]]` for `pandas` and `pandas.*` with `ignore_missing_imports = true`
3. Add temporary `[[tool.mypy.overrides]]` per-module entries with `ignore_errors = true` for all 29 files that currently have errors, so that mypy passes immediately after this ticket. Each override must have a `# TODO: remove after ticket-004` comment.

### Inputs/Props

- File: `/home/rogerio/git/cfinterface/pyproject.toml`
- Error inventory: 29 files with errors (see Current State)

### Outputs/Behavior

Add the following to pyproject.toml:

```toml
[tool.mypy]
python_version = "3.10"
disallow_untyped_defs = true
warn_return_any = true
strict_optional = true
warn_unused_configs = true
show_error_codes = true

[[tool.mypy.overrides]]
module = ["pandas", "pandas.*"]
ignore_missing_imports = true

# TODO: remove overrides below after ticket-004 fixes type annotations
[[tool.mypy.overrides]]
module = [
    "cfinterface.components.section",
    "cfinterface.components.block",
    "cfinterface.components.register",
    "cfinterface.components.line",
    "cfinterface.components.field",
    "cfinterface.components.floatfield",
    "cfinterface.components.integerfield",
    "cfinterface.components.literalfield",
    "cfinterface.components.datetimefield",
    "cfinterface.components.defaultregister",
    "cfinterface.components.defaultblock",
    "cfinterface.components.defaultsection",
    "cfinterface.components.tabular",
    "cfinterface.data.registerdata",
    "cfinterface.data.blockdata",
    "cfinterface.data.sectiondata",
    "cfinterface.files.registerfile",
    "cfinterface.files.blockfile",
    "cfinterface.files.sectionfile",
    "cfinterface.reading.registerreading",
    "cfinterface.reading.blockreading",
    "cfinterface.reading.sectionreading",
    "cfinterface.writing.registerwriting",
    "cfinterface.writing.blockwriting",
    "cfinterface.writing.sectionwriting",
    "cfinterface.adapters.components.repository",
    "cfinterface.adapters.components.line.repository",
    "cfinterface.adapters.reading.repository",
    "cfinterface.adapters.writing.repository",
    "cfinterface.versioning",
]
ignore_errors = true
```

### Error Handling

Not applicable — configuration-only change.

## Acceptance Criteria

- [ ] Given the file `/home/rogerio/git/cfinterface/pyproject.toml`, when searching for `[tool.mypy]`, then the section exists with `disallow_untyped_defs = true`, `warn_return_any = true`, and `strict_optional = true`
- [ ] Given the updated pyproject.toml, when running `uv run mypy ./cfinterface`, then mypy exits with return code 0 (success) and reports "Success: no issues found"
- [ ] Given the updated pyproject.toml, when searching for `ignore_errors = true` in the mypy overrides, then it appears exactly once, applied to a module list of 29 entries
- [ ] Given the updated pyproject.toml, when searching for the comment `# TODO: remove after ticket-004`, then the comment exists immediately before the temporary overrides block

## Implementation Guide

### Suggested Approach

1. Open `/home/rogerio/git/cfinterface/pyproject.toml`
2. Add the `[tool.mypy]` section after `[tool.pytest.ini_options]` (added by ticket-002) and before `[tool.ruff]`
3. Add the pandas overrides block
4. Add the temporary ignore_errors override block with all 29 module names
5. Run `uv run mypy ./cfinterface` and verify it passes with 0 errors
6. Verify the temporary overrides cover all files by temporarily removing them and checking that the error count matches the known 189

### Key Files to Modify

- `/home/rogerio/git/cfinterface/pyproject.toml`

### Patterns to Follow

- Use `python_version = "3.10"` to match `requires-python`
- Group mypy overrides: first third-party ignores (pandas), then temporary project ignores
- Add a clear TODO comment marking the temporary overrides for removal

### Pitfalls to Avoid

- Do NOT use `--strict` — only the three specified flags
- Do NOT add `disallow_any_generics`, `check_untyped_defs`, or other strict flags not specified
- Do NOT put `ignore_errors = true` at the top level — it must be per-module
- Do NOT forget `cfinterface.components.field` — it has 0 errors with current flags but might need to be in the list if it has `unused-ignore` issues; verify by running mypy after adding config
- Verify the exact module list by running mypy without the ignores to confirm all 29 files are covered

## Testing Requirements

### Unit Tests

Not applicable — configuration-only change.

### Integration Tests

- Run `uv run mypy ./cfinterface` and verify 0 errors reported
- Temporarily remove the `ignore_errors = true` override and run mypy to verify errors still exist (confirming the override is needed)
- Run `uv run mypy ./cfinterface --no-error-summary` to verify no output (all clean)

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None (can be done in parallel with ticket-001 and ticket-002, but logically follows)
- **Blocks**: ticket-004-fix-mypy-strict-errors (removes the temporary overrides)

## Effort Estimate

**Points**: 2
**Confidence**: High
