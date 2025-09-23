import csv
import json
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import plotly.graph_objects as go
    import plotly.offline as pyo

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    go = None
    pyo = None


@dataclass
class ReportConfig:
    title: str = "cfinterface - performance tests"
    include_charts: bool = True
    include_raw_data: bool = False
    output_format: str = "html"
    comparison_baseline: Optional[str] = None


class PerformanceReporter:
    def __init__(self, config: ReportConfig = None):
        self.config = config or ReportConfig()
        self.results = []
        self.baseline_results = []

    def load_results(self, results_file: Path) -> List[Dict[str, Any]]:
        with open(results_file, "r") as f:
            data = json.load(f)

        if "results" in data:
            return data["results"]
        return data if isinstance(data, list) else [data]

    def load_baseline(self, baseline_file: Path):
        self.baseline_results = self.load_results(baseline_file)

    def generate_report(
        self, results_files: List[Path], output_path: Path
    ) -> Path:
        all_results = []
        for file_path in results_files:
            results = self.load_results(file_path)
            all_results.extend(results)

        self.results = all_results

        if self.config.comparison_baseline:
            self.load_baseline(Path(self.config.comparison_baseline))

        if self.config.output_format == "html":
            return self._generate_html_report(output_path)
        elif self.config.output_format == "json":
            return self._generate_json_report(output_path)
        elif self.config.output_format == "csv":
            return self._generate_csv_report(output_path)
        else:
            raise ValueError(
                f"Unsupported output format: {self.config.output_format}"
            )

    def _generate_html_report(self, output_path: Path) -> Path:
        html_content = self._create_html_template()

        summary_html = self._generate_summary_html()
        html_content = html_content.replace("{SUMMARY}", summary_html)

        charts_html = ""
        if self.config.include_charts:
            charts_html = self._generate_charts_html()
        html_content = html_content.replace("{CHARTS}", charts_html)

        table_html = self._generate_results_table_html()
        html_content = html_content.replace("{RESULTS_TABLE}", table_html)

        comparison_html = ""
        if self.baseline_results:
            comparison_html = self._generate_comparison_html()
        html_content = html_content.replace("{COMPARISON}", comparison_html)

        with open(output_path, "w") as f:
            f.write(html_content)

        return output_path

    def _create_html_template(self) -> str:
        theme_styles = self._get_theme_styles()

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <style>
        {theme_styles}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .section {{ margin: 30px 0; }}
        .metric-card {{ 
            display: inline-block; 
            margin: 10px; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 5px;
            min-width: 200px;
            text-align: center;
        }}
        .chart-container {{ margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 8px 12px; border: 1px solid #ddd; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        .improvement {{ color: green; }}
        .regression {{ color: red; }}
        .neutral {{ color: #666; }}
    </style>
    {"<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>" if HAS_PLOTLY else ""}
</head>
<body>
    <div class="container">
        <h1>{self.config.title}</h1>
        <p>Generated on {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="section">
            <h2>Summary</h2>
            {{SUMMARY}}
        </div>
        
        <div class="section">
            <h2>Performance Charts</h2>
            {{CHARTS}}
        </div>
        
        <div class="section">
            <h2>Comparison with Baseline</h2>
            {{COMPARISON}}
        </div>
        
        <div class="section">
            <h2>Detailed Results</h2>
            {{RESULTS_TABLE}}
        </div>
    </div>
</body>
</html>
"""

    def _get_theme_styles(self) -> str:
        return """
            body { background-color: #ffffff; color: #000000; font-family: Arial, sans-serif; }
            .metric-card { background-color: #f9f9f9; }
        """

    def _generate_summary_html(self) -> str:
        if not self.results:
            return "<p>No results to display.</p>"

        execution_times = [r["metrics"]["execution_time"] for r in self.results]
        memory_usage = [r["metrics"]["peak_memory_mb"] for r in self.results]

        summary_stats = {
            "total_tests": len(self.results),
            "avg_execution_time": statistics.mean(execution_times),
            "median_execution_time": statistics.median(execution_times),
            "max_execution_time": max(execution_times),
            "avg_memory_usage": statistics.mean(memory_usage),
            "max_memory_usage": max(memory_usage),
        }

        system_info = self.results[0].get("system_info", {})

        html = f"""
        <div class="metric-card">
            <h3>Test Count</h3>
            <div class="metric-value">{summary_stats["total_tests"]}</div>
        </div>
        <div class="metric-card">
            <h3>Avg Execution Time</h3>
            <div class="metric-value">{summary_stats["avg_execution_time"]:.3f}s</div>
        </div>
        <div class="metric-card">
            <h3>Max Execution Time</h3>
            <div class="metric-value">{summary_stats["max_execution_time"]:.3f}s</div>
        </div>
        <div class="metric-card">
            <h3>Avg Memory Usage</h3>
            <div class="metric-value">{summary_stats["avg_memory_usage"]:.1f} MB</div>
        </div>
        <div class="metric-card">
            <h3>Max Memory Usage</h3>
            <div class="metric-value">{summary_stats["max_memory_usage"]:.1f} MB</div>
        </div>
        
        <h3>System Information</h3>
        <table>
            <tr><th>Platform</th><td>{system_info.get("platform", "Unknown")}</td></tr>
            <tr><th>Python Version</th><td>{system_info.get("python_version", "Unknown")}</td></tr>
            <tr><th>CPU Cores</th><td>{system_info.get("cpu_count", "Unknown")}</td></tr>
            <tr><th>CPU Frequency</th><td>{system_info.get("cpu_freq", 0):.0f} MHz</td></tr>
            <tr><th>Total Memory</th><td>{system_info.get("memory_total", 0) / (1024** 3):.1f} GB</td></tr>
        </table>
        """

        return html

    def _generate_charts_html(self) -> str:
        if not self.config.include_charts:
            return ""

        charts_html = ""

        if HAS_PLOTLY:
            charts_html += self._create_plotly_charts()
        else:
            charts_html = "<p>Chart library not available. Install plotly or matplotlib to enable charts.</p>"

        return charts_html

    def _create_plotly_charts(self) -> str:
        charts_html = ""

        test_names = [r["test_name"] for r in self.results]
        execution_times = [r["metrics"]["execution_time"] for r in self.results]
        memory_usage = [r["metrics"]["peak_memory_mb"] for r in self.results]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=test_names,
                y=execution_times,
                name="Execution Time (s)",
                marker_color="steelblue",
            )
        )
        fig.update_layout(
            title="Execution Time by Test",
            xaxis_title="Test Name",
            yaxis_title="Time (seconds)",
            xaxis_tickangle=-45,
        )

        chart_div = pyo.plot(fig, output_type="div", include_plotlyjs=False)
        charts_html += f'<div class="chart-container">{chart_div}</div>'

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=test_names,
                y=memory_usage,
                name="Peak Memory (MB)",
                marker_color="lightcoral",
            )
        )
        fig2.update_layout(
            title="Peak Memory Usage by Test",
            xaxis_title="Test Name",
            yaxis_title="Memory (MB)",
            xaxis_tickangle=-45,
        )

        chart_div2 = pyo.plot(fig2, output_type="div", include_plotlyjs=False)
        charts_html += f'<div class="chart-container">{chart_div2}</div>'

        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(
                x=execution_times,
                y=memory_usage,
                mode="markers+text",
                text=test_names,
                textposition="top center",
                marker=dict(size=10, color="darkgreen"),
                name="Tests",
            )
        )
        fig3.update_layout(
            title="Memory Usage vs Execution Time",
            xaxis_title="Execution Time (s)",
            yaxis_title="Peak Memory (MB)",
        )

        chart_div3 = pyo.plot(fig3, output_type="div", include_plotlyjs=False)
        charts_html += f'<div class="chart-container">{chart_div3}</div>'

        return charts_html

    def _generate_results_table_html(self) -> str:
        if not self.results:
            return "<p>No results to display.</p>"

        html = """
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Execution Time (s)</th>
                    <th>Peak Memory (MB)</th>
                    <th>CPU %</th>
                    <th>Iterations</th>
                    <th>File Size</th>
                </tr>
            </thead>
            <tbody>
        """

        for result in sorted(
            self.results,
            key=lambda r: r["metrics"]["execution_time"],
            reverse=True,
        ):
            metrics = result["metrics"]
            params = result["test_params"]

            html += f"""
                <tr>
                    <td>{result["test_name"]}</td>
                    <td>{metrics["execution_time"]:.3f}</td>
                    <td>{metrics["peak_memory_mb"]:.1f}</td>
                    <td>{metrics["cpu_percent"]:.1f}</td>
                    <td>{result["iterations"]}</td>
                    <td>{params.get("file_size", "N/A")}</td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """

        return html

    def _generate_comparison_html(self) -> str:
        if not self.baseline_results:
            return "<p>No baseline results available for comparison.</p>"

        comparisons = self._compare_with_baseline()

        html = """
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Current Time (s)</th>
                    <th>Baseline Time (s)</th>
                    <th>Time Change</th>
                    <th>Current Memory (MB)</th>
                    <th>Baseline Memory (MB)</th>
                    <th>Memory Change</th>
                </tr>
            </thead>
            <tbody>
        """

        for comp in comparisons:
            time_class = self._get_change_class(comp["time_change_percent"])
            memory_class = self._get_change_class(comp["memory_change_percent"])

            html += f"""
                <tr>
                    <td>{comp["test_name"]}</td>
                    <td>{comp["current_time"]:.3f}</td>
                    <td>{comp["baseline_time"]:.3f}</td>
                    <td class="{time_class}">{comp["time_change_percent"]:+.1f}%</td>
                    <td>{comp["current_memory"]:.1f}</td>
                    <td>{comp["baseline_memory"]:.1f}</td>
                    <td class="{memory_class}">{comp["memory_change_percent"]:+.1f}%</td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """

        return html

    def _compare_with_baseline(self) -> List[Dict[str, Any]]:
        comparisons = []

        baseline_lookup = {r["test_name"]: r for r in self.baseline_results}

        for current in self.results:
            test_name = current["test_name"]
            if test_name in baseline_lookup:
                baseline = baseline_lookup[test_name]

                current_time = current["metrics"]["execution_time"]
                baseline_time = baseline["metrics"]["execution_time"]
                time_change = (
                    (current_time - baseline_time) / baseline_time
                ) * 100

                current_memory = current["metrics"]["peak_memory_mb"]
                baseline_memory = baseline["metrics"]["peak_memory_mb"]
                memory_change = (
                    ((current_memory - baseline_memory) / baseline_memory) * 100
                    if baseline_memory > 0
                    else 0
                )

                comparisons.append({
                    "test_name": test_name,
                    "current_time": current_time,
                    "baseline_time": baseline_time,
                    "time_change_percent": time_change,
                    "current_memory": current_memory,
                    "baseline_memory": baseline_memory,
                    "memory_change_percent": memory_change,
                })

        return comparisons

    def _get_change_class(self, percent_change: float) -> str:
        if percent_change < -5:
            return "improvement"
        elif percent_change > 5:
            return "regression"
        else:
            return "neutral"

    def _generate_json_report(self, output_path: Path) -> Path:
        report_data = {
            "config": asdict(self.config),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.results,
            "summary": self._calculate_summary_stats(),
        }

        if self.baseline_results:
            report_data["comparison"] = self._compare_with_baseline()

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)

        return output_path

    def _generate_csv_report(self, output_path: Path) -> Path:
        with open(output_path, "w", newline="") as csvfile:
            fieldnames = [
                "test_name",
                "execution_time",
                "peak_memory_mb",
                "cpu_percent",
                "iterations",
                "timestamp",
                "file_size",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in self.results:
                row = {
                    "test_name": result["test_name"],
                    "execution_time": result["metrics"]["execution_time"],
                    "peak_memory_mb": result["metrics"]["peak_memory_mb"],
                    "cpu_percent": result["metrics"]["cpu_percent"],
                    "iterations": result["iterations"],
                    "timestamp": result["timestamp"],
                    "file_size": result["test_params"].get("file_size", "N/A"),
                }
                writer.writerow(row)

        return output_path

    def _calculate_summary_stats(self) -> Dict[str, Any]:
        if not self.results:
            return {}

        execution_times = [r["metrics"]["execution_time"] for r in self.results]
        memory_usage = [r["metrics"]["peak_memory_mb"] for r in self.results]

        return {
            "total_tests": len(self.results),
            "execution_time": {
                "mean": statistics.mean(execution_times),
                "median": statistics.median(execution_times),
                "min": min(execution_times),
                "max": max(execution_times),
                "std": statistics.stdev(execution_times)
                if len(execution_times) > 1
                else 0,
            },
            "memory_usage": {
                "mean": statistics.mean(memory_usage),
                "median": statistics.median(memory_usage),
                "min": min(memory_usage),
                "max": max(memory_usage),
                "std": statistics.stdev(memory_usage)
                if len(memory_usage) > 1
                else 0,
            },
        }


def generate_performance_report(
    results_files: List[Path], output_path: Path, config: ReportConfig = None
) -> Path:
    reporter = PerformanceReporter(config)
    return reporter.generate_report(results_files, output_path)
