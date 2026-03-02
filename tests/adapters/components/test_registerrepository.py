from cfinterface.adapters.components.repository import (
    TextualRepository,
    BinaryRepository,
)


def test_textual_matches_str_pattern_str_line():
    assert TextualRepository.matches(r"hello", "hello, world!") is True


def test_textual_matches_no_match():
    assert TextualRepository.matches(r"xyz", "hello, world!") is False


def test_binary_matches_bytes_pattern_bytes_line():
    assert BinaryRepository.matches(b"hello", b"hello, world!") is True


def test_binary_matches_str_pattern_bytes_line():
    assert BinaryRepository.matches(r"hello", b"hello, world!") is True


def test_binary_matches_bytes_pattern_no_match():
    assert BinaryRepository.matches(b"xyz", b"hello, world!") is False


def test_binary_matches_str_pattern_no_match():
    assert BinaryRepository.matches(r"xyz", b"hello, world!") is False
