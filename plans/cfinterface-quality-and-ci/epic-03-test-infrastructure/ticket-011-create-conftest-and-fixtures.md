# ticket-011 Create conftest.py with Shared Test Fixtures

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Create a `tests/conftest.py` file with shared pytest fixtures that eliminate duplicated setup code across the test suite. Common patterns observed include creating FloatField/IntegerField/LiteralField instances, building TabularParser configurations, creating temporary files for file I/O tests, and constructing RegisterData/BlockData/SectionData containers. Extracting these into fixtures improves test maintainability and provides a foundation for hypothesis strategies and benchmark tests.

## Anticipated Scope

- **Files likely to be modified**: `tests/conftest.py` (create), potentially `tests/components/conftest.py` (create), existing test files may optionally adopt fixtures
- **Key decisions needed**: Which fixtures to create (must analyze actual test duplication after Epics 1-2 are complete), whether to use `conftest.py` at root level only or also sub-package level, whether to use `@pytest.fixture` with session/module/function scope
- **Open questions**: Should existing tests be refactored to use fixtures (risk of breakage) or should fixtures only be used by new tests? What fixture naming convention to adopt?

## Dependencies

- **Blocked By**: ticket-002-add-pytest-configuration (markers and config must be in place)
- **Blocks**: ticket-012-add-hypothesis-field-tests, ticket-013-add-hypothesis-tabular-tests

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
