#!/usr/bin/env python3
"""Generate simple ASCII dependency graph."""

import tomllib
from pathlib import Path
from collections import defaultdict

root = Path(__file__).parent.parent
packages_dir = root / "packages"

dependencies = defaultdict(set)

# Scan packages
for pkg_dir in packages_dir.iterdir():
    if not pkg_dir.is_dir():
        continue
    pyproject = pkg_dir / "pyproject.toml"
    if not pyproject.exists():
        continue
    
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)
    
    pkg_name = data.get("project", {}).get("name", pkg_dir.name)
    deps = data.get("project", {}).get("dependencies", [])
    
    for dep in deps:
        dep_name = dep.split("[")[0].split(">")[0].split("=")[0].split("<")[0].strip()
        if dep_name.startswith("canvod-"):
            dependencies[pkg_name].add(dep_name)

# Print graph
print("canVODpy Package Dependencies")
print("=" * 50)
print()

# Foundation packages (no dependencies)
foundation = [pkg for pkg in sorted(dependencies.keys()) if not dependencies[pkg]]
foundation += [pkg_dir.name for pkg_dir in packages_dir.iterdir() 
               if pkg_dir.is_dir() and (pkg_dir / "pyproject.toml").exists()
               and pkg_dir.name not in dependencies]

print("Foundation (no dependencies):")
for pkg in sorted(set(foundation)):
    if not pkg.startswith("canvod-"):
        pkg = f"canvod-{pkg}"
    print(f"  📦 {pkg}")

print()
print("Consumers (with dependencies):")
for pkg_name, deps in sorted(dependencies.items()):
    if deps:
        deps_str = ", ".join(sorted(deps))
        print(f"  📦 {pkg_name}")
        for dep in sorted(deps):
            print(f"      └─→ {dep}")

print()
print("Summary:")
print(f"  Total packages: {len(foundation) + len([p for p in dependencies if dependencies[p]])}")
print(f"  Foundation packages: {len(foundation)}")
print(f"  Consumer packages: {len([p for p in dependencies if dependencies[p]])}")
print(f"  Total dependencies: {sum(len(d) for d in dependencies.values())}")
