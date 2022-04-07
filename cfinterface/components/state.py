from enum import Enum, auto


class ComponentState(Enum):
    NOT_FOUND = auto()
    READ_SUCCESS = auto()
    READ_ERROR = auto()
    WRITE_SUCCESS = auto()
    WRITE_ERROR = auto()
