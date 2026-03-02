import math
from typing import Any


def _is_null(value: Any) -> bool:
    """Return True if value is None, NaN, or a datetime-like null
    (e.g. pandas.NaT)."""
    if value is None:
        return True
    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        pass
    # Handle datetime-like sentinels such as pandas.NaT whose strftime raises.
    # We avoid a hard pandas import by checking for the strftime attribute and
    # attempting to call it; if it raises, the value is a null sentinel.
    if hasattr(value, "strftime"):
        try:
            value.strftime("%Y")
            return False
        except (ValueError, AttributeError, TypeError):
            return True
    return False
