#!/usr/bin/env python3
"""Dependency Graph Analyzer for canVODpy Monorepo

Analyzes package dependencies to:
1. Generate visual dependency graphs (Mermaid, Graphviz)
2. Calculate independence metrics
3. Identify circular dependencies
4. Suggest improvements for Sollbruchstellen (breaking points)

Usage:
    python scripts/analyze_dependencies.py
    python scripts/analyze_dependencies.py --format mermaid
    python scripts/analyze_dependencies.py --format dot
    python scripts/analyze_dependencies.py --metrics
"""

import argparse
from collections import defaultdict
from pathlib import Path

import tomllib


class DependencyAnalyzer:
    """Analyzes dependencies in a Python monorepo."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.packages: dict[str, dict] = {}
        self.dependencies: dict[str, set[str]] = defaultdict(set)
        self.reverse_deps: dict[str, set[str]] = defaultdict(set)

    def scan_packages(self) -> None:
        """Scan all packages in the monorepo."""
        packages_dir = self.root_dir / "packages"

        for pkg_dir in packages_dir.iterdir():
            if not pkg_dir.is_dir():
                continue

            pyproject_path = pkg_dir / "pyproject.toml"
            if not pyproject_path.exists():
                continue

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            pkg_name = data.get("project", {}).get("name", pkg_dir.name)
            self.packages[pkg_name] = {
                "path": pkg_dir,
                "data": data,
                "description": data.get("project", {}).get("description", ""),
            }

            # Extract dependencies
            deps = data.get("project", {}).get("dependencies", [])
            for dep in deps:
                # Extract package name (before version specifier)
                dep_name = dep.split("[")[0].split(">")[0].split("=")[0].split("<")[0].strip()
                # Only track internal dependencies
                if dep_name.startswith("canvod-"):
                    self.dependencies[pkg_name].add(dep_name)
                    self.reverse_deps[dep_name].add(pkg_name)

    def find_circular_dependencies(self) -> list[list[str]]:
        """Find circular dependency chains."""
        circles = []
        visited = set()

        def dfs(node: str, path: list[str]) -> None:
            if node in path:
                # Found a circle
                circle_start = path.index(node)
                circle = path[circle_start:] + [node]
                if circle not in circles:
                    circles.append(circle)
                return

            if node in visited:
                return

            visited.add(node)
            for dep in self.dependencies.get(node, []):
                dfs(dep, path + [node])

        for pkg in self.packages:
            dfs(pkg, [])

        return circles

    def calculate_metrics(self) -> dict[str, dict]:
        """Calculate independence metrics for each package."""
        metrics = {}

        for pkg_name in self.packages:
            # Afferent coupling (Ca): packages that depend on this package
            ca = len(self.reverse_deps.get(pkg_name, set()))

            # Efferent coupling (Ce): packages this package depends on
            ce = len(self.dependencies.get(pkg_name, set()))

            # Instability (I): Ce / (Ce + Ca)
            # I = 0: maximally stable (no dependencies, many dependents)
            # I = 1: maximally unstable (many dependencies, no dependents)
            instability = ce / (ce + ca) if (ce + ca) > 0 else 0

            # Independence score (custom metric)
            # Higher is better (fewer dependencies)
            total_packages = len(self.packages) - 1  # Exclude self
            independence = (
                1 - (ce / total_packages) if total_packages > 0 else 1.0
            )

            metrics[pkg_name] = {
                "afferent_coupling": ca,
                "efferent_coupling": ce,
                "instability": instability,
                "independence": independence,
                "dependents": list(self.reverse_deps.get(pkg_name, set())),
                "dependencies": list(self.dependencies.get(pkg_name, set())),
            }

        return metrics

    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram."""
        lines = ["```mermaid", "graph TD"]

        # Add style classes
        lines.append("    classDef stable fill:#90EE90,stroke:#2E8B57,stroke-width:2px")
        lines.append("    classDef unstable fill:#FFB6C1,stroke:#DC143C,stroke-width:2px")
        lines.append("    classDef balanced fill:#87CEEB,stroke:#4682B4,stroke-width:2px")

        # Add nodes with descriptions
        for pkg_name, info in self.packages.items():
            node_id = pkg_name.replace("-", "_")
            desc = info["description"][:40] + "..." if len(info["description"]) > 40 else info["description"]
            lines.append(f'    {node_id}["{pkg_name}<br/>{desc}"]')

        # Add edges
        for pkg_name, deps in self.dependencies.items():
            pkg_id = pkg_name.replace("-", "_")
            for dep in deps:
                dep_id = dep.replace("-", "_")
                lines.append(f"    {pkg_id} --> {dep_id}")

        # Apply styles based on instability
        metrics = self.calculate_metrics()
        for pkg_name, m in metrics.items():
            pkg_id = pkg_name.replace("-", "_")
            if m["instability"] < 0.3:
                lines.append(f"    class {pkg_id} stable")
            elif m["instability"] > 0.7:
                lines.append(f"    class {pkg_id} unstable")
            else:
                lines.append(f"    class {pkg_id} balanced")

        lines.append("```")
        return "\n".join(lines)

    def generate_graphviz(self) -> str:
        """Generate Graphviz DOT format."""
        lines = ["digraph dependencies {"]
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box, style=rounded];")
        lines.append("")

        metrics = self.calculate_metrics()

        # Add nodes with colors based on instability
        for pkg_name, m in metrics.items():
            label = f"{pkg_name}\\nI={m['instability']:.2f}"

            if m["instability"] < 0.3:
                color = "#90EE90"  # Green (stable)
            elif m["instability"] > 0.7:
                color = "#FFB6C1"  # Pink (unstable)
            else:
                color = "#87CEEB"  # Blue (balanced)

            lines.append(f'    "{pkg_name}" [label="{label}", fillcolor="{color}", style="filled,rounded"];')

        lines.append("")

        # Add edges
        for pkg_name, deps in self.dependencies.items():
            for dep in deps:
                lines.append(f'    "{pkg_name}" -> "{dep}";')

        lines.append("}")
        return "\n".join(lines)

    def generate_report(self) -> str:
        """Generate text report with metrics and recommendations."""
        metrics = self.calculate_metrics()
        circles = self.find_circular_dependencies()

        lines = ["# Dependency Analysis Report", ""]

        # Summary
        lines.append("## Summary")
        lines.append(f"- Total packages: {len(self.packages)}")
        lines.append(f"- Total internal dependencies: {sum(len(d) for d in self.dependencies.values())}")
        lines.append(f"- Circular dependencies: {len(circles)}")
        lines.append("")

        # Circular dependencies
        if circles:
            lines.append("## ⚠️  Circular Dependencies")
            lines.append("")
            for i, circle in enumerate(circles, 1):
                lines.append(f"{i}. {' → '.join(circle)}")
            lines.append("")
            lines.append("**Recommendation:** Break circular dependencies for better modularity.")
            lines.append("")

        # Package metrics
        lines.append("## Package Independence Metrics")
        lines.append("")
        lines.append("| Package | Dependencies | Dependents | Instability | Independence | Status |")
        lines.append("|---------|--------------|------------|-------------|--------------|--------|")

        # Sort by independence (most independent first)
        sorted_metrics = sorted(
            metrics.items(),
            key=lambda x: x[1]["independence"],
            reverse=True
        )

        for pkg_name, m in sorted_metrics:
            status = "🟢 Stable" if m["instability"] < 0.3 else "🔴 Unstable" if m["instability"] > 0.7 else "🟡 Balanced"
            lines.append(
                f"| {pkg_name} | {m['efferent_coupling']} | {m['afferent_coupling']} | "
                f"{m['instability']:.2f} | {m['independence']:.2f} | {status} |"
            )

        lines.append("")

        # Detailed analysis
        lines.append("## Detailed Analysis")
        lines.append("")

        for pkg_name, m in sorted_metrics:
            lines.append(f"### {pkg_name}")
            lines.append("")
            lines.append(f"**Description:** {self.packages[pkg_name]['description']}")
            lines.append("")
            lines.append(f"- **Efferent Coupling (Ce):** {m['efferent_coupling']} - Depends on {m['efferent_coupling']} internal packages")
            lines.append(f"- **Afferent Coupling (Ca):** {m['afferent_coupling']} - Used by {m['afferent_coupling']} internal packages")
            lines.append(f"- **Instability (I):** {m['instability']:.2f} - {'Low (stable)' if m['instability'] < 0.3 else 'High (unstable)' if m['instability'] > 0.7 else 'Medium'}")
            lines.append(f"- **Independence:** {m['independence']:.2f} - {'Highly independent' if m['independence'] > 0.8 else 'Moderately independent' if m['independence'] > 0.5 else 'Low independence'}")
            lines.append("")

            if m["dependencies"]:
                lines.append(f"**Dependencies ({len(m['dependencies'])}):** {', '.join(m['dependencies'])}")
            else:
                lines.append("**Dependencies:** None ✅")

            if m["dependents"]:
                lines.append(f"**Dependents ({len(m['dependents'])}):** {', '.join(m['dependents'])}")
            else:
                lines.append("**Dependents:** None (leaf package)")

            lines.append("")

        # Recommendations
        lines.append("## 🎯 Recommendations for Improving Independence")
        lines.append("")

        # Find packages with high coupling
        high_coupling = [
            (name, m) for name, m in metrics.items()
            if m["efferent_coupling"] > 2
        ]

        if high_coupling:
            lines.append("### High Coupling (>2 dependencies)")
            lines.append("")
            for pkg_name, m in high_coupling:
                lines.append(f"**{pkg_name}** depends on {m['efferent_coupling']} packages:")
                for dep in m["dependencies"]:
                    lines.append(f"  - {dep}")
                lines.append("")
                lines.append("  💡 **Suggestion:** Consider:")
                lines.append("  - Moving shared functionality to a common base package")
                lines.append("  - Using dependency injection instead of direct imports")
                lines.append("  - Creating interfaces/protocols for loose coupling")
                lines.append("")

        # Find leaf packages (no dependents)
        leaves = [name for name, m in metrics.items() if m["afferent_coupling"] == 0]
        if leaves:
            lines.append("### Leaf Packages (No Dependents)")
            lines.append("")
            lines.append("These packages are not used by other packages:")
            for pkg in leaves:
                lines.append(f"- {pkg}")
            lines.append("")
            lines.append("💡 **Good for independence!** These can be easily extracted.")
            lines.append("")

        # Find hub packages (many dependents)
        hubs = [
            (name, m) for name, m in metrics.items()
            if m["afferent_coupling"] > 3
        ]
        if hubs:
            lines.append("### Hub Packages (>3 Dependents)")
            lines.append("")
            for pkg_name, m in hubs:
                lines.append(f"**{pkg_name}** is used by {m['afferent_coupling']} packages:")
                for dep in m["dependents"]:
                    lines.append(f"  - {dep}")
                lines.append("")
                lines.append("  💡 **Suggestion:** Ensure this is intentional. Consider:")
                lines.append("  - Splitting into smaller, focused packages")
                lines.append("  - Moving rarely-used functionality out")
                lines.append("  - Documenting as a core/foundation package")
                lines.append("")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze monorepo dependencies")
    parser.add_argument(
        "--format",
        choices=["mermaid", "dot", "report", "all"],
        default="report",
        help="Output format"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (default: stdout)"
    )
    args = parser.parse_args()

    # Find repo root
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    # Analyze
    analyzer = DependencyAnalyzer(root_dir)
    analyzer.scan_packages()

    # Generate output
    if args.format == "mermaid":
        output = analyzer.generate_mermaid()
    elif args.format == "dot":
        output = analyzer.generate_graphviz()
    elif args.format == "report":
        output = analyzer.generate_report()
    elif args.format == "all":
        output = "# Dependency Analysis\n\n"
        output += "## Mermaid Diagram\n\n"
        output += analyzer.generate_mermaid() + "\n\n"
        output += "## Metrics Report\n\n"
        output += analyzer.generate_report()

    # Write output
    if args.output:
        args.output.write_text(output)
        print(f"✅ Written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
