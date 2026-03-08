# Epic 03 Learnings: Documentation Content

## What Was Implemented

1. **Architecture overview** (ticket-007): Created `docs/source/guides/architecture.rst` with component hierarchy, fields, adapters, versioning, and extension points.

2. **FAQ page** (ticket-008): Created `docs/source/guides/faq.rst` with 7 common questions covering custom fields, pandas integration, storage backends, versioning, debugging, and testing.

3. **Migration guide** (ticket-009): Created `docs/source/guides/migration-v1.9.rst` with before/after code examples for pandas optional dependency, StorageType enum, set_version() deprecation, and array containers.

4. **Performance tips** (ticket-010): Created `docs/source/guides/performance.rst` covering regex caching, FloatField optimization, array containers, read_many(), and TabularParser column selection.

5. **Contributing update** (ticket-011): Rewrote `docs/source/getting_started/contributing.rst` in pt-BR, fixed inewave→cfinterface URL, added uv-based setup and pre-commit hooks documentation.

## Key Learnings

- **`:orphan:` directive is essential**: New RST files not yet in a toctree need `:orphan:` as the first line to prevent `toc.not_included` warnings under `-W` flag. All 4 new guide pages use this. Ticket-013 will add toctree entries and remove `:orphan:`.

- **`:doc:` references must target existing files**: Cross-references like `:doc:\`/api/index\``will fail under`-W`if the target doesn't exist. Use plain text or`:class:` references instead.

- **All guides in `docs/source/guides/`**: New directory established for architecture, FAQ, migration, and performance pages. Contributing stays at its existing location in `getting_started/`.

- **pt-BR content convention**: All prose in Portuguese, code examples in English. Class/function names remain in English.

## Recommendations for Epic 04

- ticket-013 (index.rst restructure) must add toctree entries for all 4 guide pages AND remove their `:orphan:` directives
- ticket-012 (CONTRIBUTING.md) should reference the Sphinx contributing page for full details
