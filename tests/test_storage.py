from cfinterface.storage import StorageType


def test_storage_type_text_value():
    assert StorageType.TEXT.value == "TEXT"


def test_storage_type_binary_value():
    assert StorageType.BINARY.value == "BINARY"


def test_storage_type_text_str_comparison():
    assert StorageType.TEXT == "TEXT"


def test_storage_type_binary_str_comparison():
    assert StorageType.BINARY == "BINARY"


def test_storage_type_from_string():
    assert StorageType("TEXT") is StorageType.TEXT
    assert StorageType("BINARY") is StorageType.BINARY


def test_storage_type_import_from_package():
    from cfinterface import StorageType as ST

    assert ST.TEXT == "TEXT"
