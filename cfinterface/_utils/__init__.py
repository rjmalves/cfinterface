import math
from typing import Any


def _is_null(value: Any) -> bool:
    """Return True if value is None or NaN."""
    if value is None:
        return True
    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        return False
