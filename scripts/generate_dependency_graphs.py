#!/usr/bin/env python3
"""Generate comprehensive dependency graphs for canVODpy using pydeps.

This script creates two levels of analysis:
1. Package-level: Internal class/module dependencies within each package
2. API-level: How the umbrella package orchestrates all components + config

Usage:
    python scripts/generate_dependency_graphs.py --all
    python scripts/generate_dependency_graphs.py --package canvod-readers
    python scripts/generate_dependency_graphs.py --api
"""

import argparse
import subprocess
from pathlib import Path


class DependencyGraphGenerator:
    """Generate dependency graphs using pydeps."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.output_dir = root_dir / "docs" / "dependency-graphs"
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def generate_package_graph(
        self,
        package_name: str,
        show_classes: bool = True,
        cluster: bool = True
    ) -> None:
        """Generate internal dependency graph for a package."""
        print(f"\n🔍 Analyzing {package_name}...")

        # Convert package-name to module path (e.g., canvod-readers → canvod/readers)
        module_name = package_name.replace("-", "/")

        # Find package source directory with actual module
        pkg_dir = self.root_dir / "packages" / package_name / "src" / module_name.replace("/", ".")

        # Try alternative structure if first doesn't exist
        if not pkg_dir.exists():
            pkg_dir = self.root_dir / "packages" / package_name / "src" / "canvod" / package_name.split("-")[1]

        if not pkg_dir.exists():
            print(f"⚠️  Package directory not found: {pkg_dir}")
            return

        # Output file
        output_file = self.output_dir / f"{package_name}-internal.svg"

        # Build pydeps command (use uv run to access installed pydeps)
        cmd = [
            str(Path.home() / ".local/bin/uv"), "run", "pydeps",
            str(pkg_dir),
            "--cluster",  # Group by module
            "--max-bacon", "3",  # Show 3 levels deep
            "--noshow",  # Don't open browser
            "-o", str(output_file),
            "--exclude", "*test*,test*",  # Exclude tests
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Created {output_file.name}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate graph for {package_name}")
            print(f"   Error: {e.stderr}")

    def generate_api_graph(self) -> None:
        """Generate API orchestration graph showing umbrella package."""
        print("\n🔍 Analyzing API orchestration (umbrella package)...")

        # Find umbrella package
        api_dir = self.root_dir / "canvodpy" / "src"
        if not api_dir.exists():
            api_dir = self.root_dir / "canvodpy"

        if not api_dir.exists():
            print(f"⚠️  Umbrella package not found at {api_dir}")
            return

        # Output file
        output_file = self.output_dir / "api-orchestration.svg"

        # Build pydeps command - show how umbrella uses all packages (use uv run)
        cmd = [
            str(Path.home() / ".local/bin/uv"), "run", "pydeps",
            str(api_dir),
            "--cluster",
            "--max-bacon", "3",  # Show API → packages → internals
            "--noshow",
            "-o", str(output_file),
            "--exclude", "test*,*test*",  # Exclude tests
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Created {output_file.name}")
        except subprocess.CalledProcessError as e:
            print("❌ Failed to generate API graph")
            print(f"   Error: {e.stderr}")

    def generate_config_flow_graph(self) -> None:
        """Generate graph showing config flow through the system."""
        print("\n🔍 Analyzing configuration flow...")

        # Focus on canvod-utils (config package)
        utils_dir = self.root_dir / "packages" / "canvod-utils" / "src"
        if not utils_dir.exists():
            print("⚠️  Utils package not found")
            return

        output_file = self.output_dir / "config-flow.svg"

        cmd = [
            str(Path.home() / ".local/bin/uv"), "run", "pydeps",
            str(utils_dir),
            "--only", "canvod.utils.config",
            "--cluster",
            "--max-bacon", "3",
            "--reverse",  # Show who imports config
            "--noshow",
            "-o", str(output_file),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Created {output_file.name}")
        except subprocess.CalledProcessError as e:
            print("❌ Failed to generate config flow graph")
            print(f"   Error: {e.stderr}")

    def generate_all_packages(self, package_names: list[str]) -> None:
        """Generate graphs for all packages."""
        for pkg_name in package_names:
            self.generate_package_graph(pkg_name)

    def generate_summary(self, package_names: list[str]) -> None:
        """Generate a summary document."""
        output_file = self.output_dir / "README.md"

        lines = [
            "# Dependency Graphs",
            "",
            "Visual dependency analysis for canVODpy packages.",
            "",
            "## Package-Level Dependencies (Internal)",
            "",
            "Shows how classes and modules import each other within each package:",
            "",
        ]

        for pkg_name in package_names:
            graph_file = f"{pkg_name}-internal.svg"
            if (self.output_dir / graph_file).exists():
                lines.append(f"### {pkg_name}")
                lines.append("")
                lines.append(f"![{pkg_name} internal dependencies]({graph_file})")
                lines.append("")

        lines.extend([
            "## API Orchestration",
            "",
            "Shows how the umbrella package (canvodpy) orchestrates all components:",
            "",
            "![API Orchestration](api-orchestration.svg)",
            "",
            "## Configuration Flow",
            "",
            "Shows how configuration flows through the system:",
            "",
            "![Config Flow](config-flow.svg)",
            "",
            "## Regenerating Graphs",
            "",
            "```bash",
            "# Regenerate all graphs",
            "python scripts/generate_dependency_graphs.py --all",
            "",
            "# Regenerate specific package",
            "python scripts/generate_dependency_graphs.py --package canvod-readers",
            "",
            "# Regenerate API graph only",
            "python scripts/generate_dependency_graphs.py --api",
            "```",
            "",
            "## Reading the Graphs",
            "",
            "- **Arrows** show import direction (A → B means A imports B)",
            "- **Clusters** group related modules together",
            "- **Colors** distinguish different modules/packages",
            "",
            "**Generated:** Auto-updated during development",
        ])

        output_file.write_text("\n".join(lines))
        print(f"\n✅ Created {output_file.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate dependency graphs for canVODpy"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all graphs (packages + API + config)"
    )
    parser.add_argument(
        "--package",
        type=str,
        help="Generate graph for specific package (e.g., canvod-readers)"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Generate API orchestration graph"
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Generate configuration flow graph"
    )
    args = parser.parse_args()

    # Find repo root
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    generator = DependencyGraphGenerator(root_dir)

    # Package list
    packages = [
        "canvod-readers",
        "canvod-aux",
        "canvod-grids",
        "canvod-vod",
        "canvod-store",
        "canvod-viz",
        "canvod-utils",
    ]

    if args.all:
        print("🚀 Generating all dependency graphs...")
        generator.generate_all_packages(packages)
        generator.generate_api_graph()
        generator.generate_config_flow_graph()
        generator.generate_summary(packages)
        print("\n✨ All graphs generated in docs/dependency-graphs/")

    elif args.package:
        generator.generate_package_graph(args.package)

    elif args.api:
        generator.generate_api_graph()

    elif args.config:
        generator.generate_config_flow_graph()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
