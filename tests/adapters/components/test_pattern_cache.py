import re

from cfinterface.adapters.components.repository import _compile, _pattern_cache


def test_compile_caches_pattern():
    _pattern_cache.clear()
    p1 = _compile("test")
    p2 = _compile("test")
    assert p1 is p2


def test_compile_bytes_pattern():
    _pattern_cache.clear()
    p = _compile(b"test")
    assert isinstance(p, re.Pattern)
    assert p.search(b"this is a test") is not None


def test_compile_different_patterns():
    _pattern_cache.clear()
    p1 = _compile("foo")
    p2 = _compile("bar")
    assert p1 is not p2
    assert len(_pattern_cache) == 2
