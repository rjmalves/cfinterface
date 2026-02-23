"""Benchmark FloatField._textual_write() across format types and scenarios."""

import timeit
from cfinterface.components.floatfield import FloatField

N_WRITES = 100_000
N_REPEATS = 5


def _make_fields(size, dec, fmt, values):
    return [FloatField(size, 0, dec, format=fmt, value=v) for v in values]


def _bench_scenario(name, fields, n_writes, n_repeats):
    n_fields = len(fields)
    loops = n_writes // n_fields

    def run():
        for _ in range(loops):
            for f in fields:
                f._textual_write()

    times = timeit.repeat(run, number=1, repeat=n_repeats)
    per_write = [t / n_writes * 1e6 for t in times]
    return (
        name,
        n_writes,
        min(per_write),
        sum(per_write) / len(per_write),
        max(per_write),
    )


def run_benchmarks():
    scenarios = [
        (
            "F fits at full precision",
            _make_fields(12, 4, "F", [float(i) + 0.1234 for i in range(100)]),
        ),
        (
            "F requires precision reduction",
            _make_fields(8, 4, "F", [12345.6789 + i for i in range(100)]),
        ),
        (
            "F rounding carry",
            _make_fields(5, 2, "F", [999.99 + i * 1000 for i in range(100)]),
        ),
        (
            "E non-zero",
            _make_fields(
                12, 4, "E", [float(i) + 0.1234 for i in range(1, 101)]
            ),
        ),
        (
            "D non-zero",
            _make_fields(
                12, 4, "D", [float(i) + 0.1234 for i in range(1, 101)]
            ),
        ),
        (
            "E/D zero",
            _make_fields(12, 4, "E", [0.0] * 50)
            + _make_fields(12, 4, "D", [0.0] * 50),
        ),
    ]

    header = f"{'Scenario':<35} | {'N writes':>8} | {'min (us)':>9} | {'mean (us)':>10} | {'max (us)':>9}"
    print("FloatField._textual_write() Benchmark")
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    for name, fields in scenarios:
        result = _bench_scenario(name, fields, N_WRITES, N_REPEATS)
        print(
            f"{result[0]:<35} | {result[1]:>8} | {result[2]:>9.2f} | {result[3]:>10.2f} | {result[4]:>9.2f}"
        )


if __name__ == "__main__":
    run_benchmarks()
