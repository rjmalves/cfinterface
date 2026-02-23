from datetime import datetime
import numpy as np
from cfinterface._utils import _is_null


def test_is_null_none():
    assert _is_null(None) is True


def test_is_null_float_nan():
    assert _is_null(float("nan")) is True


def test_is_null_numpy_nan():
    assert _is_null(np.nan) is True


def test_is_null_numpy_float64_nan():
    assert _is_null(np.float64("nan")) is True


def test_is_null_numpy_float32_nan():
    assert _is_null(np.float32("nan")) is True


def test_is_null_zero():
    assert _is_null(0.0) is False


def test_is_null_integer():
    assert _is_null(42) is False


def test_is_null_negative():
    assert _is_null(-1.5) is False


def test_is_null_empty_string():
    assert _is_null("") is False


def test_is_null_string():
    assert _is_null("hello") is False


def test_is_null_datetime():
    assert _is_null(datetime(2024, 1, 1)) is False


def test_is_null_numpy_scalar():
    assert _is_null(np.float32(1.5)) is False


def test_is_null_numpy_int():
    assert _is_null(np.int32(10)) is False
