import pytest

from tests.mocks.mock_open import mock_open


@pytest.fixture()
def mock_open_seekable():
    def _factory(read_data=""):
        return mock_open(read_data=read_data)

    return _factory


@pytest.fixture()
def tmp_text_file(tmp_path):
    def _factory(content: str, name: str = "test.txt"):
        p = tmp_path / name
        p.write_text(content)
        return p

    return _factory


@pytest.fixture()
def tmp_binary_file(tmp_path):
    def _factory(content: bytes, name: str = "test.bin"):
        p = tmp_path / name
        p.write_bytes(content)
        return p

    return _factory
