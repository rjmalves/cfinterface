# ticket-002 Upgrade GitHub Actions versions

## Context

### Background

The cfinterface CI workflows use `astral-sh/setup-uv@v3` across all four workflow files. The current stable release is `@v6`. Upgrading ensures the project benefits from bug fixes, performance improvements, and continued compatibility. Additionally, `codecov/codecov-action@v4` should be upgraded to `@v5`.

### Relation to Epic

This is the second ticket in Epic 01 (CI & Developer Tooling). It modernizes the CI action versions independently of any workflow structure changes.

### Current State

All four workflow files use `astral-sh/setup-uv@v3`:

- `/home/rogerio/git/cfinterface/.github/workflows/main.yml` (line 32, line 59)
- `/home/rogerio/git/cfinterface/.github/workflows/docs.yml` (line 13)
- `/home/rogerio/git/cfinterface/.github/workflows/publish.yml` (line 17)
- `/home/rogerio/git/cfinterface/.github/workflows/benchmark.yml` (line 15)

The main workflow also uses `codecov/codecov-action@v4` (line 44) which should be `@v5`.

All files use `actions/checkout@v4` and `actions/upload-artifact@v4`, which are current.

## Specification

### Requirements

1. Replace `astral-sh/setup-uv@v3` with `astral-sh/setup-uv@v6` in all four workflow files
2. Replace `codecov/codecov-action@v4` with `codecov/codecov-action@v5` in `main.yml`
3. No other changes to workflow logic, steps, or job structure

### Inputs/Props

Four YAML workflow files as listed above.

### Outputs/Behavior

All workflow files reference the latest stable action versions. No behavioral changes -- the workflows run identically but with newer action implementations.

### Error Handling

Not applicable -- this is a version bump with no logic changes.

## Acceptance Criteria

- [ ] Given `.github/workflows/main.yml`, when the file is searched for `setup-uv@`, then all matches show `@v6` and none show `@v3`
- [ ] Given `.github/workflows/docs.yml`, when the file is searched for `setup-uv@`, then the match shows `@v6`
- [ ] Given `.github/workflows/publish.yml`, when the file is searched for `setup-uv@`, then the match shows `@v6`
- [ ] Given `.github/workflows/benchmark.yml`, when the file is searched for `setup-uv@`, then the match shows `@v6`
- [ ] Given `.github/workflows/main.yml`, when the file is searched for `codecov-action@`, then the match shows `@v5`

## Implementation Guide

### Suggested Approach

1. Open each of the four workflow files
2. Find-and-replace `astral-sh/setup-uv@v3` with `astral-sh/setup-uv@v6`
3. In `main.yml`, find-and-replace `codecov/codecov-action@v4` with `codecov/codecov-action@v5`
4. Verify no other action references need updating (`actions/checkout@v4` and `actions/upload-artifact@v4` are current)

### Key Files to Modify

- `/home/rogerio/git/cfinterface/.github/workflows/main.yml` (MODIFY)
- `/home/rogerio/git/cfinterface/.github/workflows/docs.yml` (MODIFY)
- `/home/rogerio/git/cfinterface/.github/workflows/publish.yml` (MODIFY)
- `/home/rogerio/git/cfinterface/.github/workflows/benchmark.yml` (MODIFY)

### Patterns to Follow

Simple version string replacement. No structural changes.

### Pitfalls to Avoid

- Do NOT change any workflow logic, job names, or step ordering
- Do NOT upgrade `actions/checkout` or `actions/upload-artifact` -- they are already at latest stable
- Do NOT modify the `peaceiris/actions-gh-pages` version in `docs.yml` -- that is handled by ticket-003

## Testing Requirements

### Unit Tests

Not applicable.

### Integration Tests

- Verify all four workflow files are valid YAML after changes
- Push to a branch and confirm CI workflows trigger and pass

### E2E Tests

Not applicable.

## Dependencies

- **Blocked By**: None
- **Blocks**: None

## Effort Estimate

**Points**: 1
**Confidence**: High
