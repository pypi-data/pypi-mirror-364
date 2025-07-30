#!/usr/bin/env python3
"""
Generate performance summary reports from wheel test results.
Can output to console, markdown, or GitHub Actions summary format.
"""

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Generate performance summaries from test results."""

    def __init__(self, results_dir: Path):
        self.results_dir = Path(results_dir)
        self.results = self._load_all_results()

    def _load_all_results(self) -> List[Dict]:
        """Load all test results from the results directory."""
        results: List[Dict] = []

        # Check if results directory exists
        if not self.results_dir.exists():
            logger.warning(f"Results directory does not exist: {self.results_dir}")
            return results

        # Look for result files
        result_files = list(self.results_dir.rglob("test_results.json"))
        if not result_files:
            logger.warning(f"No test_results.json files found in {self.results_dir}")
            return results

        for result_file in result_files:
            try:
                with open(result_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        results.extend(data)
                    else:
                        results.append(data)
                logger.debug(
                    f"Loaded {len(data) if isinstance(data, list) else 1} "
                    f"results from {result_file}"
                )
            except Exception as e:
                logger.warning(f"Failed to load results from {result_file}: {e}")

        logger.info(
            f"Loaded {len(results)} test results from {len(result_files)} files"
        )
        return results

    def get_statistics(self) -> Dict:
        """Get summary statistics."""
        total_wheels = len(self.results)
        successful_wheels = sum(1 for r in self.results if r.get("status") == "SUCCESS")
        failed_wheels = total_wheels - successful_wheels

        # Group by platform
        platform_stats: Dict[str, int] = defaultdict(int)
        for result in self.results:
            platform = result.get("platform", "unknown")
            platform_stats[platform] += 1

        # Group by Python version
        python_stats: Dict[str, int] = defaultdict(int)
        for result in self.results:
            python_version = result.get("target_python", "unknown")
            python_stats[python_version] += 1

        # Performance statistics
        execution_times = [
            r.get("execution_time", 0)
            for r in self.results
            if r.get("status") == "SUCCESS" and r.get("execution_time")
        ]

        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        min_time = min(execution_times) if execution_times else 0
        max_time = max(execution_times) if execution_times else 0

        return {
            "total_wheels": total_wheels,
            "successful_wheels": successful_wheels,
            "failed_wheels": failed_wheels,
            "platform_stats": dict(platform_stats),
            "python_stats": dict(python_stats),
            "avg_execution_time": avg_time,
            "min_execution_time": min_time,
            "max_execution_time": max_time,
            "total_execution_times": len(execution_times),
        }

    def generate_markdown_table(self) -> str:
        """Generate a markdown table of all results."""
        lines = [
            "| Platform | Architecture | Wheel | Target Python | Actual Python | "
            "Execution Time | Status |",
            "|----------|-------------|-------|---------------|---------------|"
            "----------------|--------|",
        ]

        for result in sorted(
            self.results, key=lambda x: (x.get("platform", ""), x.get("wheel", ""))
        ):
            platform = result.get("platform", "N/A")
            architecture = result.get("architecture", "N/A")
            wheel = result.get("wheel", "N/A")
            target_python = result.get("target_python", "N/A")
            actual_python = result.get("actual_python", "N/A")
            exec_time = result.get("execution_time", 0)
            status = result.get("status", "UNKNOWN")

            # Format execution time
            if exec_time and exec_time > 0:
                time_str = f"{exec_time:.4f}s"
            else:
                time_str = "N/A"

            # Status icon
            if status == "SUCCESS":
                status_icon = "✅"
            elif status == "FAILED":
                status_icon = "❌"
            else:
                status_icon = "⚠️"

            # Check for Python version mismatch
            if target_python != "N/A" and actual_python != "N/A":
                if not actual_python.startswith(target_python):
                    status_icon = "⚠️"

            lines.append(
                f"| {platform} | {architecture} | {wheel} | {target_python} | "
                f"{actual_python} | {time_str} | {status_icon} |"
            )

        return "\n".join(lines)

    def generate_platform_breakdown(self) -> str:
        """Generate a platform-specific breakdown."""
        lines = ["## Platform-Specific Details\n"]

        # Group results by platform
        platform_results = defaultdict(list)
        for result in self.results:
            platform = result.get("platform", "unknown")
            platform_results[platform].append(result)

        for platform, results in sorted(platform_results.items()):
            lines.append(f"### {platform} ({len(results)} wheels)\n")

            # Group by Python version
            python_results = defaultdict(list)
            for result in results:
                python_version = result.get("target_python", "unknown")
                python_results[python_version].append(result)

            for python_version, py_results in sorted(python_results.items()):
                lines.append(
                    f"#### Python {python_version} ({len(py_results)} wheels)\n"
                )

                for result in py_results:
                    wheel = result.get("wheel", "unknown")
                    architecture = result.get("architecture", "N/A")
                    exec_time = result.get("execution_time", 0)
                    status = result.get("status", "UNKNOWN")
                    actual_python = result.get("actual_python", "N/A")
                    target_python = result.get("target_python", "N/A")

                    # Check version match
                    version_match = "✅"
                    if target_python != "N/A" and actual_python != "N/A":
                        if not actual_python.startswith(target_python):
                            version_match = "⚠️"

                    if status != "SUCCESS":
                        version_match = "❌"

                    # Format execution time
                    if exec_time and exec_time > 0:
                        time_str = f"{exec_time:.4f}s"
                    else:
                        time_str = "N/A"

                    lines.append(
                        f"- **{wheel}** ({architecture}): {time_str} {version_match}"
                    )

                lines.append("")

        return "\n".join(lines)

    def generate_performance_plots_list(self) -> str:
        """Generate a list of available performance plots."""
        lines = [
            "### Available Performance Plots:",
            "",
            "📊 Each plot shows the displacement field computed for a 1000x1000 "
            "grid with 2 triangular dislocation elements.",
            "",
            "🔽 **Download the plots from the workflow artifacts** to view the "
            "performance visualizations.",
            "",
        ]

        # Find all PNG files in the results directory
        png_files = list(self.results_dir.rglob("*.png"))

        if not png_files:
            lines.append("No performance plots found.")
            return "\n".join(lines)

        # Group by platform for better organization
        platform_groups: Dict[str, List[Tuple[str, str]]] = {}
        for png_file in sorted(png_files):
            filename = png_file.name

            # Extract platform and Python version info
            parts = filename.replace("tde_test_", "").replace(".png", "").split("_")

            python_version = "unknown"
            platform_info = "unknown"

            for part in parts:
                if part.startswith("cp") and len(part) >= 4:
                    try:
                        py_ver = part[2:]
                        if py_ver.isdigit() and len(py_ver) >= 2:
                            python_version = f"{py_ver[0]}.{py_ver[1:]}"
                    except (IndexError, ValueError):
                        pass

            if len(parts) >= 3:
                # Extract platform from filename parts
                platform_parts = []
                for part in parts:
                    if any(
                        plat in part
                        for plat in ["linux", "win", "macos", "manylinux", "musllinux"]
                    ):
                        platform_parts.append(part)
                        break

                if platform_parts:
                    platform_info = platform_parts[0]
                else:
                    platform_info = "_".join(parts[-2:])

            if platform_info not in platform_groups:
                platform_groups[platform_info] = []

            platform_groups[platform_info].append((filename, python_version))

        # Display organized by platform
        for platform, files in sorted(platform_groups.items()):
            lines.append(f"#### 🖥️ {platform.replace('_', ' ').title()}")
            lines.append("")

            for filename, python_version in sorted(files):
                lines.append(f"- **{filename}** (Python {python_version})")

            lines.append("")

        lines.extend(
            [
                "---",
                "",
                "💡 **Viewing the plots:**",
                "The plots can be found in the build artifact wheel-test-results-*.",
                "",
            ]
        )

        return "\n".join(lines)

    def generate_console_summary(self) -> str:
        """Generate a console-friendly summary."""
        stats = self.get_statistics()

        lines = [
            "=" * 80,
            "TDE Wheel Performance Test Summary",
            "=" * 80,
            f"Total wheels tested: {stats['total_wheels']}",
            f"Successful: {stats['successful_wheels']}",
            f"Failed: {stats['failed_wheels']}",
            "",
            "Platform breakdown:",
        ]

        for platform, count in sorted(stats["platform_stats"].items()):
            lines.append(f"  - {platform}: {count} wheels")

        lines.extend(
            [
                "",
                "Python version breakdown:",
            ]
        )

        for python_version, count in sorted(stats["python_stats"].items()):
            lines.append(f"  - Python {python_version}: {count} wheels")

        if stats["total_execution_times"] > 0:
            lines.extend(
                [
                    "",
                    "Performance statistics:",
                    f"  - Average execution time: {stats['avg_execution_time']:.4f}s",
                    f"  - Fastest: {stats['min_execution_time']:.4f}s",
                    f"  - Slowest: {stats['max_execution_time']:.4f}s",
                ]
            )

        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_github_actions_summary(self) -> str:
        """Generate a GitHub Actions summary."""
        stats = self.get_statistics()

        # Determine if this is a combined summary (multiple platforms) or individual
        unique_platforms = set(r.get("platform", "unknown") for r in self.results)
        is_combined = len(unique_platforms) > 1

        title = (
            "Combined Performance Summary"
            if is_combined
            else "TDE Individual Wheel Performance Test Results"
        )

        lines = [
            f"# 🚀 {title}",
            "",
            "Comprehensive performance comparison across all platforms and "
            "Python versions:",
            "",
            self.generate_markdown_table(),
            "",
            "## Summary Statistics",
            f"- **Total wheels tested:** {stats['total_wheels']}",
            f"- **Successful wheels:** {stats['successful_wheels']}",
            f"- **Failed wheels:** {stats['failed_wheels']}",
            "",
            "### Platform Breakdown:",
        ]

        for platform, count in sorted(stats["platform_stats"].items()):
            lines.append(f"- **{platform}:** {count} wheels")

        lines.extend(
            [
                "",
                "### Python Version Breakdown:",
            ]
        )

        for python_version, count in sorted(stats["python_stats"].items()):
            lines.append(f"- **Python {python_version}:** {count} wheels")

        if stats["total_execution_times"] > 0:
            lines.extend(
                [
                    "",
                    "### Performance Statistics:",
                    f"- **Average execution time:** {stats['avg_execution_time']:.4f}s",
                    f"- **Fastest wheel:** {stats['min_execution_time']:.4f}s",
                    f"- **Slowest wheel:** {stats['max_execution_time']:.4f}s",
                ]
            )

        lines.extend(
            [
                "",
                "## Performance Notes",
                "- All tests use a 1000x1000 grid (1,000,000 observation points) "
                "with 2 triangular dislocation elements",
                "- Timing includes displacement matrix computation only",
                "- Each wheel tested in isolated virtual environment",
                "",
                "## Generated Visualizations",
                "Performance visualization plots have been generated for each "
                "individual wheel and uploaded as artifacts.",
                "",
                self.generate_performance_plots_list(),
                "",
                self.generate_platform_breakdown(),
                "",
                "## Legend",
                "- ✅ = Test passed with exact Python version match",
                "- ⚠️ = Test passed but Python version mismatch "
                "(wheel built for different version)",
                "- ❌ = Test failed",
            ]
        )

        return "\n".join(lines)

    def save_summary(self, output_file: Path, format_type: str = "markdown"):
        """Save summary to file."""
        if format_type == "github":
            content = self.generate_github_actions_summary()
        elif format_type == "console":
            content = self.generate_console_summary()
        else:  # markdown
            content = self.generate_github_actions_summary()

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Summary saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate performance summary from test results"
    )
    parser.add_argument(
        "--results-dir",
        "-r",
        type=Path,
        required=True,
        help="Directory containing test results",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file (prints to console if not specified)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "console", "github"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--github-summary",
        action="store_true",
        help="Write to GitHub Actions summary (GITHUB_STEP_SUMMARY)",
    )

    args = parser.parse_args()

    generator = SummaryGenerator(args.results_dir)

    if args.github_summary:
        # Write to GitHub Actions summary
        github_summary_file = os.getenv("GITHUB_STEP_SUMMARY")
        if github_summary_file:
            summary = generator.generate_github_actions_summary()
            with open(github_summary_file, "a", encoding="utf-8") as f:
                f.write(summary)
            logger.info("Summary written to GitHub Actions summary")
        else:
            logger.warning("GITHUB_STEP_SUMMARY environment variable not set")

    if args.output:
        generator.save_summary(args.output, args.format)
    else:
        # Print to console only if not writing to GitHub summary
        if not args.github_summary:
            try:
                # Try to reconfigure stdout for UTF-8 if possible (Python 3.7+)
                if hasattr(sys.stdout, "reconfigure"):
                    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
            except (AttributeError, OSError):
                pass

            try:
                if args.format == "console":
                    print(generator.generate_console_summary())
                elif args.format == "github":
                    print(generator.generate_github_actions_summary())
                else:
                    print(generator.generate_github_actions_summary())
            except UnicodeEncodeError:
                # Fallback for Windows console encoding issues
                logger.warning(
                    "Console encoding doesn't support Unicode characters. "
                    "Summary written to GitHub Actions only."
                )

    return 0


if __name__ == "__main__":
    sys.exit(main())
