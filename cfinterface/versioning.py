from typing import Any, NamedTuple


class SchemaVersion(NamedTuple):
    """Associates a version key with its component types and an optional
    description."""

    key: str
    components: list[type]
    description: str = ""


def resolve_version(
    requested: str,
    versions: dict[str, list[type]],
) -> list[type] | None:
    """
    Return the component list for the most recent version key <= requested.

    Keys are compared lexicographically. Returns None when requested is
    older than every available key.
    """
    available_versions = sorted(versions.keys())
    recent_versions = [ver for ver in available_versions if requested >= ver]
    if recent_versions:
        return versions.get(recent_versions[-1])
    return None


class VersionMatchResult(NamedTuple):
    """Diagnostic result from :func:`validate_version`.

    ``matched`` is True when all expected types were found and
    ``default_ratio`` is strictly below the validation threshold.
    ``default_ratio`` is 1.0 when data is empty.
    """

    matched: bool
    expected_types: list[type]
    found_types: list[type]
    missing_types: list[type]
    unexpected_types: list[type]
    default_ratio: float


def validate_version(
    data: Any,
    expected_types: list[type],
    default_type: type,
    threshold: float = 0.5,
) -> VersionMatchResult:
    """
    Validate file data against expected component types.

    Uses exact type comparison (``type(item) is default_type``) so that
    subclasses of the default type count as real components. ``matched`` is
    True when no expected types are missing and ``default_ratio < threshold``.
    """
    expected_set = set(expected_types)
    found_set: set = set()
    default_count = 0
    total = 0

    for item in data:
        total += 1
        item_type = type(item)
        if item_type is default_type:
            default_count += 1
        else:
            found_set.add(item_type)

    default_ratio = default_count / total if total > 0 else 1.0
    found_types = sorted(found_set, key=lambda t: t.__name__)
    missing_types = sorted(expected_set - found_set, key=lambda t: t.__name__)
    unexpected_types = sorted(
        found_set - expected_set, key=lambda t: t.__name__
    )
    matched = len(missing_types) == 0 and default_ratio < threshold

    return VersionMatchResult(
        matched=matched,
        expected_types=list(expected_types),
        found_types=found_types,
        missing_types=missing_types,
        unexpected_types=unexpected_types,
        default_ratio=default_ratio,
    )
