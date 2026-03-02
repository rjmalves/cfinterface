from cfinterface.storage import StorageType
from cfinterface.adapters.components.repository import (
    factory as component_factory,
    TextualRepository as ComponentTextual,
    BinaryRepository as ComponentBinary,
)
from cfinterface.adapters.components.line.repository import (
    factory as line_factory,
    TextualRepository as LineTextual,
    BinaryRepository as LineBinary,
)
from cfinterface.adapters.reading.repository import (
    factory as reading_factory,
    TextualRepository as ReadingTextual,
    BinaryRepository as ReadingBinary,
)
from cfinterface.adapters.writing.repository import (
    factory as writing_factory,
    TextualRepository as WritingTextual,
    BinaryRepository as WritingBinary,
)


def test_component_factory_with_enum():
    assert component_factory(StorageType.TEXT) is ComponentTextual
    assert component_factory(StorageType.BINARY) is ComponentBinary


def test_component_factory_with_string():
    assert component_factory("TEXT") is ComponentTextual
    assert component_factory("BINARY") is ComponentBinary


def test_line_factory_with_enum():
    assert line_factory(StorageType.TEXT) is LineTextual
    assert line_factory(StorageType.BINARY) is LineBinary


def test_reading_factory_with_enum():
    assert reading_factory(StorageType.TEXT) is ReadingTextual
    assert reading_factory(StorageType.BINARY) is ReadingBinary


def test_writing_factory_with_enum():
    assert writing_factory(StorageType.TEXT) is WritingTextual
    assert writing_factory(StorageType.BINARY) is WritingBinary


def test_factory_default_fallback():
    assert component_factory("") is ComponentTextual
    assert component_factory("INVALID") is ComponentTextual
