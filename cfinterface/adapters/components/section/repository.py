from abc import ABC
from typing import Dict, Type


class Repository(ABC):
    pass


class BinaryRepository(Repository):
    pass


class TextualRepository(Repository):
    pass


def factory(kind: str) -> Type[Repository]:
    mappings: Dict[str, Type[Repository]] = {
        "TEXT": TextualRepository,
        "BINARY": BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
