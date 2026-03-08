import warnings

from cfinterface.storage import StorageType, _ensure_storage_type


def test_ensure_storage_type_enum_no_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _ensure_storage_type(StorageType.TEXT)
        assert result is StorageType.TEXT
        assert len(w) == 0


def test_ensure_storage_type_string_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _ensure_storage_type("TEXT")
        assert result is StorageType.TEXT
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "StorageType.TEXT" in str(w[0].message)


def test_ensure_storage_type_empty_string_no_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _ensure_storage_type("")
        assert result == ""
        assert len(w) == 0


def test_ensure_storage_type_binary_string_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _ensure_storage_type("BINARY")
        assert result is StorageType.BINARY
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)


def test_file_subclass_with_string_storage_warns():
    from cfinterface.files.registerfile import RegisterFile

    class StringStorageFile(RegisterFile):
        STORAGE = "TEXT"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        StringStorageFile()
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "StorageType.TEXT" in str(w[0].message)


def test_file_subclass_with_enum_storage_no_warning():
    from cfinterface.files.registerfile import RegisterFile

    class EnumStorageFile(RegisterFile):
        STORAGE = StorageType.TEXT

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        EnumStorageFile()
        assert len(w) == 0
