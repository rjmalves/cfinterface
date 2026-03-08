# ticket-003 Migrate docs deployment to official GitHub Pages action

## Context

### Background

The cfinterface docs workflow (`.github/workflows/docs.yml`) uses `peaceiris/actions-gh-pages@v4` to deploy Sphinx-built HTML to GitHub Pages. The official GitHub-recommended approach uses `actions/upload-pages-artifact` + `actions/deploy-pages`, which provides better integration with GitHub's deployment environment, deployment status tracking, and eliminates the dependency on a third-party action.

### Relation to Epic

This is the third and final ticket in Epic 01 (CI & Developer Tooling). It completes the CI modernization by migrating the docs deployment to the official GitHub Pages action.

### Current State

File `/home/rogerio/git/cfinterface/.github/workflows/docs.yml` currently:

- Builds Sphinx docs with `sphinx-build -W`
- Deploys using `peaceiris/actions-gh-pages@v4` with `publish_branch: gh-pages`, `github_token`, and `force_orphan: true`
- Runs on push to `main` and `workflow_dispatch`
- Single job: `docs`

## Specification

### Requirements

1. Replace the `peaceiris/actions-gh-pages@v4` deploy step with `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4`
2. Split into two jobs: `build` and `deploy` (deploy depends on build)
3. Add required top-level `permissions` for `pages: write` and `id-token: write`
4. Add `concurrency` group to prevent concurrent deployments
5. Configure `environment` on the deploy job with `name: github-pages` and `url: ${{ steps.deployment.outputs.page_url }}`
6. Preserve the `workflow_dispatch` trigger alongside the push trigger

### Inputs/Props

Current workflow file at `/home/rogerio/git/cfinterface/.github/workflows/docs.yml`.

### Outputs/Behavior

- The workflow builds docs and deploys them to GitHub Pages using the official action
- Deployment status is visible in the GitHub repository's Environments tab
- Concurrent deployments are prevented by a concurrency group

### Error Handling

- If the Sphinx build fails (exit code non-zero from `-W` flag), the build job fails and deploy is skipped
- If the deploy job fails, the deployment status shows as failed in the Environments tab

## Acceptance Criteria

- [ ] Given `.github/workflows/docs.yml`, when the file is read, then it contains no reference to `peaceiris/actions-gh-pages`
- [ ] Given `.github/workflows/docs.yml`, when the file is read, then it contains `actions/upload-pages-artifact@v3` in the build job and `actions/deploy-pages@v4` in the deploy job
- [ ] Given `.github/workflows/docs.yml`, when the top-level `permissions` key is read, then it includes `pages: write` and `id-token: write`
- [ ] Given `.github/workflows/docs.yml`, when the `concurrency` key is read, then it specifies a group name and `cancel-in-progress: false`
- [ ] Given `.github/workflows/docs.yml`, when the deploy job is read, then it has `needs: build` and an `environment` with `name: github-pages`

## Implementation Guide

### Suggested Approach

Write the new `docs.yml` with this structure:

```yaml
name: Docs

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v6
      - name: Set up Python
        run: uv python install 3.12
      - name: Install the project
        run: uv sync --all-extras --dev
      - name: Sphinx build
        run: uv run python -m sphinx -M html docs/source docs/build -W
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/build/html

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Key Files to Modify

- `/home/rogerio/git/cfinterface/.github/workflows/docs.yml` (MODIFY: complete rewrite)

### Patterns to Follow

The two-job pattern (build + deploy) is the standard pattern recommended by GitHub for Pages deployments. The deploy job references the artifact uploaded by the build job.

### Pitfalls to Avoid

- Do NOT forget the `if` condition on the deploy job -- `workflow_dispatch` should build but only deploy from `main`
- Do NOT set `cancel-in-progress: true` -- this could cancel an in-progress deployment
- Do NOT forget `contents: read` permission -- checkout requires it
- The `actions/upload-pages-artifact` expects the `path` to be the directory containing the built HTML, which is `docs/build/html` (not `docs/build`)
- Note: also use `setup-uv@v6` here since ticket-002 upgrades the version (if implemented in order) or this ticket should be self-consistent regardless

## Testing Requirements

### Unit Tests

Not applicable.

### Integration Tests

- Trigger the workflow via `workflow_dispatch` and verify the build job succeeds
- Verify the deploy job runs when pushed to `main`

### E2E Tests

- After deployment, verify the docs site is accessible at `https://rjmalves.github.io/cfinterface/`

## Dependencies

- **Blocked By**: None (can be done in parallel with ticket-001 and ticket-002, but should use `@v6` for setup-uv)
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: High
