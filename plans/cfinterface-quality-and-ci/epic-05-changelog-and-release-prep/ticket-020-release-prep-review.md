# ticket-020 Final Release Preparation Review

## Context

### Background

With all architecture improvements and quality/CI enhancements committed, and the CHANGELOG created by ticket-019, the project needs a final consistency review before the v1.9.0 release. This ticket verifies that version numbers, classifiers, metadata, and build artifacts are all consistent and correct. It does not perform the actual release (that is triggered by creating a GitHub release tag).

### Relation to Epic

This is the second and final ticket in Epic 05 (CHANGELOG and Release Preparation). It depends on ticket-019 (CHANGELOG must exist for version consistency checks). After this ticket, the project is ready for the maintainer to create a GitHub release tag.

### Current State

- `cfinterface/__init__.py` has `__version__ = "1.9.0"`.
- `pyproject.toml` uses `dynamic = ["version"]` with `[tool.hatch.version] path = "cfinterface/__init__.py"` (version is sourced from `__init__.py`).
- `CHANGELOG.md` was created by ticket-019 with a `## [1.9.0] - Unreleased` section.
- `cfinterface/py.typed` exists (PEP 561 marker).
- `pyproject.toml` includes classifiers for Python 3.10-3.14, `Typing :: Typed`, `Development Status :: 4 - Beta`.
- CI workflows: `main.yml` (tests + lint), `docs.yml` (Sphinx build + deploy), `publish.yml` (PyPI publish on release), `benchmark.yml` (manual dispatch).
- `publish.yml` triggers on `release: types: [created]` and publishes via PyPI trusted publisher.
- The `[tool.hatch.build.targets.wheel] include` lists `"cfinterface/"`.

## Specification

### Requirements

1. **Version consistency**: Verify that the version string `"1.9.0"` appears in `cfinterface/__init__.py` and that `pyproject.toml` sources its version dynamically from that file via `[tool.hatch.version]`. Verify that `CHANGELOG.md` contains a `## [1.9.0]` section header.
2. **Classifier accuracy**: Verify that `pyproject.toml` classifiers include all Python versions in the CI test matrix (3.10, 3.11, 3.12, 3.13, 3.14) and that `Typing :: Typed` is present (since `py.typed` exists).
3. **PEP 561 compliance**: Verify that `cfinterface/py.typed` exists and that it would be included in the built wheel (the `[tool.hatch.build.targets.wheel] include` directive covers `"cfinterface/"`).
4. **Build artifact inspection**: Build the wheel using `uv build` and inspect it with `unzip -l` to confirm that `cfinterface/py.typed` is included and no unexpected files are present.
5. **CI workflow consistency**: Verify that all four workflow files (`main.yml`, `docs.yml`, `publish.yml`, `benchmark.yml`) use the same Python installer (`uv`) and that `publish.yml` runs tests before publishing.
6. **Documentation link check**: Verify that the `[project.urls]` in `pyproject.toml` point to correct URLs (Documentation: `https://rjmalves.github.io/cfinterface/`, Repository: `https://github.com/rjmalves/cfinterface/`).
7. **Comparison links in CHANGELOG**: Verify that `CHANGELOG.md` contains comparison links at the bottom referencing the correct GitHub repository URL for `[Unreleased]` and `[1.9.0]` sections.

### Inputs/Props

- `cfinterface/__init__.py` (version string)
- `pyproject.toml` (metadata, classifiers, build config, tool config)
- `CHANGELOG.md` (version section, comparison links)
- `cfinterface/py.typed` (existence check)
- `.github/workflows/main.yml`, `docs.yml`, `publish.yml`, `benchmark.yml` (CI consistency)

### Outputs/Behavior

This ticket produces no file changes if everything is consistent. If inconsistencies are found, the ticket produces targeted fixes to the affected files. The expected outcome is that all checks pass with zero corrections needed, given that earlier epics already established correct values.

### Error Handling

If any inconsistency is found (e.g., version mismatch, missing classifier, py.typed not in wheel), the fix must be applied directly to the affected file and documented in the commit message. Do not silently skip inconsistencies.

## Acceptance Criteria

- [ ] Given `cfinterface/__init__.py`, when reading the `__version__` variable, then its value is `"1.9.0"`.
- [ ] Given `pyproject.toml`, when reading `[tool.hatch.version]`, then `path` is `"cfinterface/__init__.py"` (confirming dynamic version sourcing from `__init__.py`).
- [ ] Given `CHANGELOG.md`, when searching for version section headers, then it contains a line matching `## [1.9.0]`.
- [ ] Given `pyproject.toml` classifiers, when checking for Python version classifiers, then `Programming Language :: Python :: 3.10` through `Programming Language :: Python :: 3.14` are all present (5 version-specific classifiers).
- [ ] Given the output of `uv build`, when listing the wheel contents with `unzip -l dist/cfinterface-1.9.0-py3-none-any.whl`, then `cfinterface/py.typed` appears in the file listing.

## Implementation Guide

### Suggested Approach

Execute the following checks in order, fixing any issues found:

1. **Version check**: Read `cfinterface/__init__.py` and confirm `__version__ = "1.9.0"`. Read `pyproject.toml` and confirm `[tool.hatch.version] path = "cfinterface/__init__.py"`. Read `CHANGELOG.md` and confirm `## [1.9.0]` section exists.
2. **Classifier check**: Read `pyproject.toml` classifiers list and confirm all five Python version classifiers (3.10-3.14) are present, plus `Typing :: Typed` and `Development Status :: 4 - Beta`.
3. **PEP 561 check**: Confirm `cfinterface/py.typed` exists on disk. Confirm `[tool.hatch.build.targets.wheel] include` contains `"cfinterface/"`.
4. **Build and inspect**: Run `uv build` in the project root. Run `unzip -l dist/cfinterface-*.whl` and verify `cfinterface/py.typed` is in the listing. Verify no unexpected files are included (e.g., `tests/`, `plans/`, `benchmarks/`).
5. **CI check**: Read all four workflow files and confirm they all use `astral-sh/setup-uv@v3` and `uv python install`. Confirm `publish.yml` runs `uv run pytest` before `uv build`.
6. **URL check**: Read `[project.urls]` from `pyproject.toml` and confirm Documentation and Repository URLs are correct.
7. **CHANGELOG links check**: Read the bottom of `CHANGELOG.md` and confirm comparison links use the correct base URL `https://github.com/rjmalves/cfinterface/compare/`.

### Key Files to Modify

- Potentially `cfinterface/__init__.py` (only if version is wrong)
- Potentially `pyproject.toml` (only if classifiers or metadata are wrong)
- Potentially `CHANGELOG.md` (only if comparison links are missing or incorrect)

In the expected case, no files need modification.

### Patterns to Follow

- This is a verification ticket. The primary action is reading and checking files, not writing new code.
- If a fix is needed, make the minimal targeted change and document what was wrong in the commit message.

### Pitfalls to Avoid

- Do not change the version number from `1.9.0` unless explicitly instructed by the maintainer.
- Do not set a release date in `CHANGELOG.md` (the maintainer sets it when creating the release).
- Do not modify CI workflow logic beyond fixing inconsistencies (e.g., do not add new CI steps).
- Do not clean up the `dist/` directory after `uv build` if it did not exist before; leave it for `.gitignore` to handle.

### Out of Scope

- Actually creating the GitHub release or git tag.
- Pushing to PyPI.
- Modifying README.md content.
- Running the full test suite (CI handles this).

## Testing Requirements

### Unit Tests

Not applicable (this is a verification/review ticket).

### Integration Tests

Not applicable.

### Manual Verification

- Run `uv build` and inspect the wheel contents.
- Confirm all 7 checks in the suggested approach pass without issues.

## Dependencies

- **Blocked By**: ticket-019-create-changelog.md (CHANGELOG must exist for version consistency check)
- **Blocks**: None (final ticket in the plan)

## Effort Estimate

**Points**: 1
**Confidence**: High
