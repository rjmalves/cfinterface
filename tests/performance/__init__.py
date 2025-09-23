"""
Performance Testing Framework for CFInterface

This module provides a comprehensive performance testing framework for cfinterface,
designed to benchmark read/write operations, memory usage, and I/O patterns across
different file types and sizes.
"""

import gc
import json
import platform
import shutil
import tempfile
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional

import numpy as np
import pytest

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None


@dataclass
class SystemInfo:
    """System information for benchmarking context"""

    python_version: str
    platform: str
    cpu_count: int
    cpu_freq: float
    memory_total: int
    memory_available: int
    disk_io_counters: Dict[str, Any]

    @classmethod
    def collect(cls) -> "SystemInfo":
        """Collect current system information"""
        if not HAS_PSUTIL:
            return cls(
                python_version=platform.python_version(),
                platform=f"{platform.system()} {platform.release()}",
                cpu_count=1,
                cpu_freq=0.0,
                memory_total=0,
                memory_available=0,
                disk_io_counters={},
            )

        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()

        return cls(
            python_version=platform.python_version(),
            platform=f"{platform.system()} {platform.release()}",
            cpu_count=psutil.cpu_count(),
            cpu_freq=cpu_freq.current if cpu_freq else 0.0,
            memory_total=memory.total,
            memory_available=memory.available,
            disk_io_counters=disk_io._asdict() if disk_io else {},
        )


@dataclass
class PerformanceMetrics:
    execution_time: float
    peak_memory_mb: float
    memory_delta_mb: float
    cpu_percent: float
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    gc_collections: Dict[int, int] = field(default_factory=dict)
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Result of a benchmark run"""

    test_name: str
    test_params: Dict[str, Any]
    metrics: PerformanceMetrics
    system_info: SystemInfo
    timestamp: float
    iterations: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "test_name": self.test_name,
            "test_params": self.test_params,
            "metrics": {
                "execution_time": self.metrics.execution_time,
                "peak_memory_mb": self.metrics.peak_memory_mb,
                "memory_delta_mb": self.metrics.memory_delta_mb,
                "cpu_percent": self.metrics.cpu_percent,
                "disk_read_bytes": self.metrics.disk_read_bytes,
                "disk_write_bytes": self.metrics.disk_write_bytes,
                "gc_collections": self.metrics.gc_collections,
                "custom_metrics": self.metrics.custom_metrics,
            },
            "system_info": {
                "python_version": self.system_info.python_version,
                "platform": self.system_info.platform,
                "cpu_count": self.system_info.cpu_count,
                "cpu_freq": self.system_info.cpu_freq,
                "memory_total": self.system_info.memory_total,
                "memory_available": self.system_info.memory_available,
                "disk_io_counters": self.system_info.disk_io_counters,
            },
            "timestamp": self.timestamp,
            "iterations": self.iterations,
        }


class PerformanceProfiler:
    def __init__(self, collect_memory: bool = True, collect_cpu: bool = True):
        self.collect_memory = collect_memory
        self.collect_cpu = collect_cpu
        self.start_time = 0.0
        self.end_time = 0.0
        self.peak_memory = 0.0
        self.memory_delta = 0.0
        self.cpu_percent = 0.0
        self.gc_before = {}
        self.gc_after = {}
        self.disk_io_before = None
        self.disk_io_after = None

    def __enter__(self) -> "PerformanceProfiler":
        if self.collect_memory:
            tracemalloc.start()
            gc.collect()  #
            self.gc_before = {i: gc.get_count()[i] for i in range(3)}

        if HAS_PSUTIL:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.disk_io_before = disk_io

        self.start_time = time.perf_counter()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()

        if HAS_PSUTIL:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.disk_io_after = disk_io

        if self.collect_memory:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            self.peak_memory = peak / (1024 * 1024)
            self.memory_delta = current / (1024 * 1024)

            self.gc_after = {i: gc.get_count()[i] for i in range(3)}

        if self.collect_cpu and HAS_PSUTIL:
            self.cpu_percent = psutil.cpu_percent()

    def get_metrics(self) -> PerformanceMetrics:
        disk_read = 0
        disk_write = 0

        if self.disk_io_before and self.disk_io_after:
            disk_read = (
                self.disk_io_after.read_bytes - self.disk_io_before.read_bytes
            )
            disk_write = (
                self.disk_io_after.write_bytes - self.disk_io_before.write_bytes
            )

        gc_collections = {}
        if self.gc_before and self.gc_after:
            gc_collections = {
                i: self.gc_after[i] - self.gc_before[i] for i in range(3)
            }

        return PerformanceMetrics(
            execution_time=self.end_time - self.start_time,
            peak_memory_mb=self.peak_memory,
            memory_delta_mb=self.memory_delta,
            cpu_percent=self.cpu_percent,
            disk_read_bytes=disk_read,
            disk_write_bytes=disk_write,
            gc_collections=gc_collections,
        )


class BenchmarkRunner:
    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.results: List[BenchmarkResult] = []
        self.system_info = SystemInfo.collect()

    def benchmark(
        self,
        test_name: str,
        iterations: int = 1,
        warmup_iterations: int = 0,
        **test_params,
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                for _ in range(warmup_iterations):
                    func(*args, **kwargs)
                    gc.collect()

                all_metrics = []
                for _ in range(iterations):
                    with PerformanceProfiler() as profiler:
                        result = func(*args, **kwargs)

                    metrics = profiler.get_metrics()
                    all_metrics.append(metrics)

                    gc.collect()

                avg_metrics = self._average_metrics(all_metrics)

                benchmark_result = BenchmarkResult(
                    test_name=test_name,
                    test_params=test_params,
                    metrics=avg_metrics,
                    system_info=self.system_info,
                    timestamp=time.time(),
                    iterations=iterations,
                )

                self.results.append(benchmark_result)
                return result

            return wrapper

        return decorator

    def _average_metrics(
        self, metrics_list: List[PerformanceMetrics]
    ) -> PerformanceMetrics:
        if not metrics_list:
            return PerformanceMetrics(0, 0, 0, 0)

        return PerformanceMetrics(
            execution_time=np.mean([m.execution_time for m in metrics_list]),
            peak_memory_mb=np.mean([m.peak_memory_mb for m in metrics_list]),
            memory_delta_mb=np.mean([m.memory_delta_mb for m in metrics_list]),
            cpu_percent=np.mean([m.cpu_percent for m in metrics_list]),
            disk_read_bytes=int(
                np.mean([m.disk_read_bytes for m in metrics_list])
            ),
            disk_write_bytes=int(
                np.mean([m.disk_write_bytes for m in metrics_list])
            ),
            gc_collections={
                i: int(
                    np.mean([m.gc_collections.get(i, 0) for m in metrics_list])
                )
                for i in range(3)
            },
        )

    def save_results(self, filename: Optional[str] = None) -> Path:
        if not filename:
            timestamp = int(time.time())
            filename = f"benchmark_results_{timestamp}.json"

        filepath = self.results_dir / filename

        results_data = {
            "system_info": self.system_info.__dict__,
            "results": [result.to_dict() for result in self.results],
            "summary": self._generate_summary(),
        }

        with open(filepath, "w") as f:
            json.dump(results_data, f, indent=2)

        return filepath

    def _generate_summary(self) -> Dict[str, Any]:
        if not self.results:
            return {}

        return {
            "total_tests": len(self.results),
            "total_execution_time": sum(
                r.metrics.execution_time for r in self.results
            ),
            "peak_memory_usage": max(
                r.metrics.peak_memory_mb for r in self.results
            ),
            "avg_memory_usage": np.mean([
                r.metrics.peak_memory_mb for r in self.results
            ]),
            "slowest_test": max(
                self.results, key=lambda r: r.metrics.execution_time
            ).test_name,
            "memory_intensive_test": max(
                self.results, key=lambda r: r.metrics.peak_memory_mb
            ).test_name,
        }


@contextmanager
def temporary_test_directory() -> Iterator[Path]:
    temp_dir = Path(tempfile.mkdtemp(prefix="cfinterface_perf_"))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "performance: mark test as a performance benchmark"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        if any(
            keyword in item.name.lower()
            for keyword in ["large", "stress", "memory"]
        ):
            item.add_marker(pytest.mark.slow)


def pytest_addoption(parser):
    parser.addoption(
        "--results-dir",
        action="store",
        default=None,
        help="Directory where performance tests should save results",
    )


@pytest.fixture(scope="session")
def results_dir(request) -> Optional[Path]:
    val = request.config.getoption("results_dir")
    return Path(val) if val else None
