import pytest

from cfinterface.versioning import SchemaVersion, resolve_version


class A:
    pass


class B:
    pass


class C:
    pass


def test_resolve_version_exact_match():
    assert resolve_version("v1", {"v1": [A], "v2": [B]}) == [A]


def test_resolve_version_between_versions():
    assert resolve_version("v1.5", {"v1": [A], "v2": [B]}) == [A]


def test_resolve_version_above_all():
    assert resolve_version("v3", {"v1": [A], "v2": [B]}) == [B]


def test_resolve_version_below_all():
    assert resolve_version("v0", {"v1": [A], "v2": [B]}) is None


def test_resolve_version_empty_dict():
    assert resolve_version("v1", {}) is None


def test_resolve_version_numeric_keys():
    # Lexicographic comparison: '28.12' >= '28' but '28.12' < '28.16'
    assert resolve_version(
        "28.12", {"28": [A], "28.16": [B], "29.4.1": [C]}
    ) == [A]


def test_resolve_version_numeric_exact():
    assert resolve_version("28.16", {"28": [A], "28.16": [B]}) == [B]


def test_schema_version_construction():
    sv = SchemaVersion(key="v1", components=[A], description="initial")
    assert sv.key == "v1"
    assert sv.components == [A]
    assert sv.description == "initial"


def test_schema_version_default_description():
    assert SchemaVersion(key="v1", components=[A]).description == ""


def test_schema_version_immutability():
    sv = SchemaVersion(key="v1", components=[A])
    with pytest.raises(AttributeError):
        sv.key = "v2"  # type: ignore[misc]


def test_schema_version_equality():
    sv1 = SchemaVersion(key="v1", components=[A], description="release")
    sv2 = SchemaVersion(key="v1", components=[A], description="release")
    assert sv1 == sv2


def test_import_from_top_level():
    from cfinterface import SchemaVersion as SV  # noqa: F401
    from cfinterface import resolve_version as rv

    assert SV is SchemaVersion
    assert rv is resolve_version


from cfinterface.versioning import (  # noqa: E402
    VersionMatchResult,
    validate_version,
)


class TypeA:
    pass


class TypeB:
    pass


class DefaultType:
    pass


def test_version_match_result_construction():
    r = VersionMatchResult(True, [TypeA], [TypeA], [], [], 0.0)
    assert r.matched is True
    assert r.expected_types == [TypeA]
    assert r.default_ratio == 0.0


def test_validate_version_all_matched():
    items = [TypeA(), TypeB(), DefaultType()]
    result = validate_version(items, [TypeA, TypeB], DefaultType)
    assert result.matched is True
    assert result.missing_types == []
    assert result.default_ratio == pytest.approx(1 / 3)


def test_validate_version_missing_type():
    items = [TypeA(), DefaultType()]
    result = validate_version(items, [TypeA, TypeB], DefaultType)
    assert result.matched is False
    assert TypeB in result.missing_types


def test_validate_version_all_defaults():
    items = [DefaultType(), DefaultType()]
    result = validate_version(items, [TypeA, TypeB], DefaultType)
    assert result.matched is False
    assert result.default_ratio == 1.0
    assert set(result.missing_types) == {TypeA, TypeB}


def test_validate_version_high_default_ratio_below_threshold():
    items = [TypeA(), TypeB(), DefaultType(), DefaultType(), DefaultType()]
    result = validate_version(items, [TypeA, TypeB], DefaultType, threshold=0.8)
    assert result.matched is True  # 0.6 < 0.8 and no missing types


def test_validate_version_high_default_ratio_above_threshold():
    items = [TypeA(), TypeB(), DefaultType(), DefaultType(), DefaultType()]
    result = validate_version(items, [TypeA, TypeB], DefaultType, threshold=0.5)
    assert result.matched is False  # 0.6 >= 0.5


def test_validate_version_unexpected_types():
    items = [TypeA(), TypeB()]
    result = validate_version(items, [TypeA], DefaultType)
    assert TypeB in result.unexpected_types


def test_validate_version_empty_data():
    items = []
    result = validate_version(items, [TypeA], DefaultType)
    assert result.default_ratio == 1.0
    assert result.matched is False


def test_import_version_match_result():
    from cfinterface import VersionMatchResult as VMR  # noqa: F401
    from cfinterface import validate_version as vv

    assert VMR is not None
    assert vv is not None
