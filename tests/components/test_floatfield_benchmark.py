"""pytest-benchmark tests for FloatField._textual_write() performance."""

import pytest

from cfinterface.components.floatfield import FloatField


def _make_fields(size, dec, fmt, values):
    return [FloatField(size, 0, dec, format=fmt, value=v) for v in values]


def _write_all(fields):
    for f in fields:
        f._textual_write()


@pytest.mark.benchmark
def test_bench_f_fits_full_precision(benchmark):
    fields = _make_fields(12, 4, "F", [float(i) + 0.1234 for i in range(100)])
    benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


@pytest.mark.benchmark
def test_bench_f_precision_reduction(benchmark):
    fields = _make_fields(8, 4, "F", [12345.6789 + i for i in range(100)])
    benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


@pytest.mark.benchmark
def test_bench_f_rounding_carry(benchmark):
    fields = _make_fields(5, 2, "F", [999.99 + i * 1000 for i in range(100)])
    benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


@pytest.mark.benchmark
def test_bench_e_non_zero(benchmark):
    fields = _make_fields(
        12, 4, "E", [float(i) + 0.1234 for i in range(1, 101)]
    )
    benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


@pytest.mark.benchmark
def test_bench_d_non_zero(benchmark):
    fields = _make_fields(
        12, 4, "D", [float(i) + 0.1234 for i in range(1, 101)]
    )
    benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)


@pytest.mark.benchmark
def test_bench_ed_zero(benchmark):
    fields = _make_fields(12, 4, "E", [0.0] * 50) + _make_fields(
        12, 4, "D", [0.0] * 50
    )
    benchmark.pedantic(_write_all, args=(fields,), rounds=10, iterations=100)
