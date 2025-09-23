import cProfile
import functools
import io
import pstats
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from memory_profiler import LineProfiler

    HAS_MEMORY_PROFILER = True
except ImportError:
    HAS_MEMORY_PROFILER = False
    memory_profile = None
    LineProfiler = None


@dataclass
class ProfileResult:
    function_name: str
    total_time: float
    call_count: int
    cumulative_time: float
    per_call_time: float
    memory_usage: List[Tuple[float, float]] = field(
        default_factory=list
    )  # (time, memory_mb)
    line_stats: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    hotspots: List[Tuple[str, float, int]] = field(
        default_factory=list
    )  # (function, time, calls)


class CProfileProfiler:
    def __init__(self):
        self.profiler = None
        self.stats = None

    def start(self):
        self.profiler = cProfile.Profile()
        self.profiler.enable()

    def stop(self):
        if self.profiler:
            self.profiler.disable()

            s = io.StringIO()
            ps = pstats.Stats(self.profiler, stream=s)
            ps.sort_stats("cumulative")
            ps.print_stats()

            self.stats = s.getvalue()

    def get_stats(self, limit: int = 20) -> Dict[str, Any]:
        if not self.profiler:
            return {}

        ps = pstats.Stats(self.profiler)
        ps.sort_stats("cumulative")

        hotspots = []
        for func_info, (
            call_count,
            _,
            total_time,
            cumulative_time,
        ) in ps.stats.items():
            filename, line_num, func_name = func_info
            if "cfinterface" in filename:
                hotspots.append({
                    "function": f"{Path(filename).name}:{line_num}({func_name})",
                    "calls": call_count,
                    "total_time": total_time,
                    "cumulative_time": cumulative_time,
                    "per_call_time": total_time / call_count
                    if call_count > 0
                    else 0,
                })

        hotspots.sort(key=lambda x: x["cumulative_time"], reverse=True)

        return {
            "hotspots": hotspots[:limit],
            "total_calls": sum(stats[0] for stats in ps.stats.values()),
            "total_time": sum(stats[2] for stats in ps.stats.values()),
            "raw_stats": self.stats,
        }


class MemoryProfiler:
    def __init__(self, precision: int = 1):
        self.precision = precision
        self.snapshots = []
        self.line_profiler = None

        if HAS_MEMORY_PROFILER:
            self.line_profiler = LineProfiler()

    def start(self):
        tracemalloc.start()
        if self.line_profiler:
            self.line_profiler.enable()

    def stop(self):
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        if self.line_profiler:
            self.line_profiler.disable()

    def take_snapshot(self):
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            self.snapshots.append(snapshot)

    def get_memory_usage(self) -> Dict[str, Any]:
        if not self.snapshots:
            return {}

        snapshot = self.snapshots[-1]
        top_stats = snapshot.statistics("lineno")

        memory_hotspots = []
        for stat in top_stats[:20]:
            memory_hotspots.append({
                "file": stat.traceback.format()[-1]
                if stat.traceback.format()
                else "unknown",
                "size_mb": stat.size / (1024 * 1024),
                "count": stat.count,
            })

        total_memory = sum(stat.size for stat in top_stats) / (1024 * 1024)

        return {
            "total_memory_mb": total_memory,
            "memory_hotspots": memory_hotspots,
            "snapshot_count": len(self.snapshots),
        }

    def compare_snapshots(
        self, snapshot1_idx: int = 0, snapshot2_idx: int = -1
    ) -> Dict[str, Any]:
        if len(self.snapshots) < 2:
            return {}

        snapshot1 = self.snapshots[snapshot1_idx]
        snapshot2 = self.snapshots[snapshot2_idx]

        top_stats = snapshot2.compare_to(snapshot1, "lineno")

        differences = []
        for stat in top_stats[:10]:
            differences.append({
                "file": stat.traceback.format()[-1]
                if stat.traceback.format()
                else "unknown",
                "size_diff_mb": stat.size_diff / (1024 * 1024),
                "count_diff": stat.count_diff,
            })

        return {
            "differences": differences,
            "total_size_diff_mb": sum(stat.size_diff for stat in top_stats)
            / (1024 * 1024),
        }


class IOProfiler:
    def __init__(self):
        self.io_operations = []
        self.original_open = None
        self.monitoring = False

    def start(self):
        if self.monitoring:
            return

        self.original_open = __builtins__["open"]
        self.io_operations = []

        def monitored_open(*args, **kwargs):
            operation = {
                "args": args,
                "kwargs": kwargs,
                "mode": kwargs.get("mode", args[1] if len(args) > 1 else "r"),
                "file": args[0] if args else "unknown",
            }
            self.io_operations.append(operation)

            return self.original_open(*args, **kwargs)

        __builtins__["open"] = monitored_open
        self.monitoring = True

    def stop(self):
        if self.monitoring and self.original_open:
            __builtins__["open"] = self.original_open
            self.monitoring = False

    def get_io_stats(self) -> Dict[str, Any]:
        if not self.io_operations:
            return {}

        read_ops = [op for op in self.io_operations if "r" in op["mode"]]
        write_ops = [
            op
            for op in self.io_operations
            if "w" in op["mode"] or "a" in op["mode"]
        ]
        binary_ops = [op for op in self.io_operations if "b" in op["mode"]]

        files_accessed = {}
        for op in self.io_operations:
            file_path = op["file"]
            if file_path not in files_accessed:
                files_accessed[file_path] = {"read": 0, "write": 0, "binary": 0}

            if "r" in op["mode"]:
                files_accessed[file_path]["read"] += 1
            if "w" in op["mode"] or "a" in op["mode"]:
                files_accessed[file_path]["write"] += 1
            if "b" in op["mode"]:
                files_accessed[file_path]["binary"] += 1

        return {
            "total_operations": len(self.io_operations),
            "read_operations": len(read_ops),
            "write_operations": len(write_ops),
            "binary_operations": len(binary_ops),
            "files_accessed": files_accessed,
            "unique_files": len(files_accessed),
        }


class ComprehensiveProfiler:
    def __init__(
        self,
        enable_cpu: bool = True,
        enable_memory: bool = True,
        enable_io: bool = True,
    ):
        self.enable_cpu = enable_cpu
        self.enable_memory = enable_memory
        self.enable_io = enable_io

        self.cpu_profiler = CProfileProfiler() if enable_cpu else None
        self.memory_profiler = MemoryProfiler() if enable_memory else None
        self.io_profiler = IOProfiler() if enable_io else None

        self.started = False

    def start(self):
        if self.started:
            return

        if self.cpu_profiler:
            self.cpu_profiler.start()

        if self.memory_profiler:
            self.memory_profiler.start()
            self.memory_profiler.take_snapshot()

        if self.io_profiler:
            self.io_profiler.start()

        self.started = True

    def stop(self):
        if not self.started:
            return

        if self.memory_profiler:
            self.memory_profiler.take_snapshot()
            self.memory_profiler.stop()

        if self.cpu_profiler:
            self.cpu_profiler.stop()

        if self.io_profiler:
            self.io_profiler.stop()

        self.started = False

    def get_comprehensive_report(self) -> Dict[str, Any]:
        report = {"cpu_profile": {}, "memory_profile": {}, "io_profile": {}}

        if self.cpu_profiler:
            report["cpu_profile"] = self.cpu_profiler.get_stats()

        if self.memory_profiler:
            report["memory_profile"] = self.memory_profiler.get_memory_usage()
            if len(self.memory_profiler.snapshots) >= 2:
                report["memory_profile"]["growth"] = (
                    self.memory_profiler.compare_snapshots()
                )

        if self.io_profiler:
            report["io_profile"] = self.io_profiler.get_io_stats()

        return report


@contextmanager
def profile_performance(
    enable_cpu: bool = True, enable_memory: bool = True, enable_io: bool = True
):
    profiler = ComprehensiveProfiler(enable_cpu, enable_memory, enable_io)

    try:
        profiler.start()
        yield profiler
    finally:
        profiler.stop()


def profile_function(cpu: bool = True, memory: bool = True, io: bool = True):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with profile_performance(cpu, memory, io) as profiler:
                result = func(*args, **kwargs)

                if not hasattr(func, "_profile_results"):
                    func._profile_results = []

                func._profile_results.append(
                    profiler.get_comprehensive_report()
                )

                return result

        return wrapper

    return decorator


def memory_usage_over_time(
    func: Callable, interval: float = 0.1
) -> List[Tuple[float, float]]:
    if not HAS_MEMORY_PROFILER:
        return []

    import threading
    import time

    memory_data = []
    monitoring = threading.Event()

    def monitor_memory():
        start_time = time.time()
        while not monitoring.is_set():
            try:
                import psutil

                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024 * 1024)
                elapsed_time = time.time() - start_time
                memory_data.append((elapsed_time, memory_mb))
            except ImportError:
                if tracemalloc.is_tracing():
                    current, _ = tracemalloc.get_traced_memory()
                    memory_mb = current / (1024 * 1024)
                    elapsed_time = time.time() - start_time
                    memory_data.append((elapsed_time, memory_mb))

            time.sleep(interval)

    monitor_thread = threading.Thread(target=monitor_memory)
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        func()
        return memory_data
    finally:
        monitoring.set()
        monitor_thread.join(timeout=1)


def create_profiling_report(
    profile_data: Dict[str, Any], output_path: Optional[Path] = None
) -> str:
    report_lines = []

    report_lines.append("=" * 80)
    report_lines.append("cfinterface profiling report")
    report_lines.append("=" * 80)

    if "cpu_profile" in profile_data and profile_data["cpu_profile"]:
        cpu_data = profile_data["cpu_profile"]
        report_lines.append("\nCPU Profile:")
        report_lines.append("-" * 40)
        report_lines.append(f"Total calls: {cpu_data.get('total_calls', 0)}")
        report_lines.append(f"Total time: {cpu_data.get('total_time', 0):.3f}s")

        if "hotspots" in cpu_data:
            report_lines.append("\nTop CPU Hotspots:")
            for i, hotspot in enumerate(cpu_data["hotspots"][:10], 1):
                report_lines.append(
                    f"{i:2d}. {hotspot['function']:<50} "
                    f"{hotspot['cumulative_time']:>8.3f}s ({hotspot['calls']:>6} calls)"
                )

    if "memory_profile" in profile_data and profile_data["memory_profile"]:
        memory_data = profile_data["memory_profile"]
        report_lines.append("\nMemory Profile:")
        report_lines.append("-" * 40)
        report_lines.append(
            f"Total memory: {memory_data.get('total_memory_mb', 0):.1f} MB"
        )

        if "memory_hotspots" in memory_data:
            report_lines.append("\nTop Memory Consumers:")
            for i, hotspot in enumerate(memory_data["memory_hotspots"][:10], 1):
                report_lines.append(
                    f"{i:2d}. {hotspot['file']:<50} "
                    f"{hotspot['size_mb']:>8.1f} MB ({hotspot['count']:>6} allocs)"
                )

        if "growth" in memory_data:
            growth = memory_data["growth"]
            report_lines.append(
                f"\nMemory Growth: {growth.get('total_size_diff_mb', 0):.1f} MB"
            )

    if "io_profile" in profile_data and profile_data["io_profile"]:
        io_data = profile_data["io_profile"]
        report_lines.append("\nI/O Profile:")
        report_lines.append("-" * 40)
        report_lines.append(
            f"Total operations: {io_data.get('total_operations', 0)}"
        )
        report_lines.append(
            f"Read operations: {io_data.get('read_operations', 0)}"
        )
        report_lines.append(
            f"Write operations: {io_data.get('write_operations', 0)}"
        )
        report_lines.append(f"Files accessed: {io_data.get('unique_files', 0)}")

    report_lines.append("=" * 80)

    report_text = "\n".join(report_lines)

    if output_path:
        with open(output_path, "w") as f:
            f.write(report_text)

    return report_text
