import argparse
import sys
from pathlib import Path
from typing import List

import pytest

from tests.performance.reporting import (
    ReportConfig,
    generate_performance_report,
)


def run_benchmarks(
    test_patterns: List[str] = None,
    output_dir: Path = None,
    include_slow: bool = False,
    profile: bool = False,
) -> Path:
    if output_dir is None:
        output_dir = Path.cwd() / "performance_results"
    output_dir.mkdir(exist_ok=True, parents=True)

    pytest_args = [
        str(Path(__file__).parent / "test_benchmarks.py"),
        "-v",
        "-s",
        "--tb=short",
        "--results-dir",
        str(output_dir),
    ]
    marker_expr = "performance"

    if test_patterns:
        for pattern in test_patterns:
            pytest_args.extend(["-k", pattern])

    if include_slow:
        marker_expr = "performance or slow"

    pytest_args.extend(["-m", marker_expr])

    if profile:
        pytest_args.extend(["--profile"])

    print("Running performance benchmarks...")
    print(f"Command: pytest {' '.join(pytest_args)}")

    exit_code = pytest.main(pytest_args)

    if exit_code != 0:
        print(f"Some tests failed with exit code {exit_code}")

    return output_dir


def generate_report(
    results_dir: Path,
    output_path: Path = None,
    baseline_path: Path = None,
    format: str = "html",
) -> Path:
    result_files = list(results_dir.glob("benchmark_results_*.json"))

    if not result_files:
        print(f"No benchmark result files found in {results_dir}")
        return None

    print(f"Found {len(result_files)} result files")

    if output_path is None:
        timestamp = max(
            result_files, key=lambda p: p.stat().st_mtime
        ).stem.split("_")[-1]
        output_path = results_dir / f"performance_report_{timestamp}.{format}"

    config = ReportConfig(
        output_format=format,
        comparison_baseline=str(baseline_path) if baseline_path else None,
        include_charts=True,
    )

    report_path = generate_performance_report(result_files, output_path, config)
    return report_path


def main():
    parser = argparse.ArgumentParser(
        description="CFInterface Performance Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all performance tests
  python -m tests.performance.runner

  # Run only register file tests
  python -m tests.performance.runner --pattern register

  # Run tests including slow ones and generate HTML report
  python -m tests.performance.runner --slow --report-format html

  # Generate report from existing results
  python -m tests.performance.runner --report-only --results-dir ./results

  # Compare with baseline
  python -m tests.performance.runner --baseline ./baseline_results.json
        """,
    )

    parser.add_argument(
        "--pattern",
        "-p",
        action="append",
        help="Test name patterns to run (can be used multiple times)",
    )

    parser.add_argument(
        "--slow", action="store_true", help="Include slow-running tests"
    )

    parser.add_argument(
        "--profile", action="store_true", help="Enable detailed profiling"
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        help="Output directory for results (default: ./performance_results)",
    )

    parser.add_argument(
        "--report-format",
        choices=["html", "json", "csv"],
        default="html",
        help="Report format (default: html)",
    )

    parser.add_argument("--report-title", help="Custom title for the report")

    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate report from existing results",
    )

    parser.add_argument(
        "--results-dir",
        type=Path,
        help="Directory containing existing results (for --report-only)",
    )

    parser.add_argument(
        "--baseline", type=Path, help="Baseline results file for comparison"
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Reduce output verbosity"
    )

    args = parser.parse_args()

    if args.report_only and not args.results_dir:
        parser.error("--report-only requires --results-dir")

    if args.baseline and not args.baseline.exists():
        parser.error(f"Baseline file not found: {args.baseline}")

    try:
        if args.report_only:
            report_path = generate_report(
                results_dir=args.results_dir,
                baseline_path=args.baseline,
                format=args.report_format,
            )

            if report_path:
                print(f"\nReport generated successfully: {report_path}")
            else:
                print("Failed to generate report")
                return 1

        else:
            results_dir = run_benchmarks(
                test_patterns=args.pattern,
                output_dir=args.output_dir,
                include_slow=args.slow,
                profile=args.profile,
            )

            report_path = generate_report(
                results_dir=results_dir,
                baseline_path=args.baseline,
                format=args.report_format,
            )

            if report_path:
                print("\nPerformance testing completed!")
                print(f"Results: {results_dir}")
                print(f"Report: {report_path}")
            else:
                print(
                    "Performance testing completed, but report generation failed"
                )
                return 1

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if not args.quiet:
            import traceback

            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
