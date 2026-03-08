from cfinterface.adapters.components.line.repository import (
    BinaryRepository as LineBinary,
)
from cfinterface.adapters.components.line.repository import (
    TextualRepository as LineTextual,
)
from cfinterface.adapters.components.line.repository import (
    factory as line_factory,
)
from cfinterface.adapters.components.repository import (
    BinaryRepository as ComponentBinary,
)
from cfinterface.adapters.components.repository import (
    TextualRepository as ComponentTextual,
)
from cfinterface.adapters.components.repository import (
    factory as component_factory,
)
from cfinterface.adapters.reading.repository import (
    BinaryRepository as ReadingBinary,
)
from cfinterface.adapters.reading.repository import (
    TextualRepository as ReadingTextual,
)
from cfinterface.adapters.reading.repository import (
    factory as reading_factory,
)
from cfinterface.adapters.writing.repository import (
    BinaryRepository as WritingBinary,
)
from cfinterface.adapters.writing.repository import (
    TextualRepository as WritingTextual,
)
from cfinterface.adapters.writing.repository import (
    factory as writing_factory,
)
from cfinterface.storage import StorageType


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
