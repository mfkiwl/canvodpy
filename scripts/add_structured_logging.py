#!/usr/bin/env python3
"""Script to add structured logging throughout canvodpy codebase.

This script adds import statements and replaces print() calls with log.info/error calls.
Run this as a first pass, then manually review and enhance with proper event names.
"""

import re
from pathlib import Path

# Files to update in Phase 1
PHASE1_FILES = [
    "canvodpy/src/canvodpy/orchestrator/pipeline.py",
    "canvodpy/src/canvodpy/orchestrator/processor.py",
    "canvodpy/src/canvodpy/api.py",
    "canvodpy/src/canvodpy/functional.py",
    "canvodpy/src/canvodpy/factories.py",
]

# Pattern to detect if logging is already imported
LOGGING_IMPORT_PATTERN = r"from canvodpy\.logging import get_logger"

# Pattern to find print statements (excluding comments)
PRINT_PATTERN = r"^(\s*)print\((.*)\)(\s*#.*)?$"


def add_logging_import(content: str, module_path: str) -> str:
    """Add logging import if not present."""
    if LOGGING_IMPORT_PATTERN in content:
        return content, False

    # Find the last import statement
    lines = content.split("\n")
    last_import_idx = 0

    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i

    # Insert after last import
    lines.insert(last_import_idx + 1, "")
    lines.insert(last_import_idx + 2, "from canvodpy.logging import get_logger")

    return "\n".join(lines), True


def replace_prints_with_logging(content: str) -> tuple[str, int]:
    """Replace print() statements with log.info() calls."""
    lines = content.split("\n")
    replacements = 0

    for i, line in enumerate(lines):
        # Skip comments
        if line.strip().startswith("#"):
            continue

        match = re.match(PRINT_PATTERN, line)
        if match:
            indent = match.group(1)
            args = match.group(2)
            comment = match.group(3) or ""

            # Convert to log.info
            # This is a simple replacement - manual review needed for proper event names
            lines[i] = f'{indent}log.info("event", message={args}){comment}'
            replacements += 1

    return "\n".join(lines), replacements


def add_logger_initialization_to_class(content: str, class_name: str) -> str:
    """Add self.log initialization to __init__ method."""
    # Find __init__ method
    init_pattern = rf"(class {class_name}.*?def __init__\(self.*?\):.*?)"

    # This is complex - better to do manually
    return content


def process_file(file_path: Path) -> dict:
    """Process a single file to add logging."""
    if not file_path.exists():
        return {"status": "skip", "reason": "not found"}

    content = file_path.read_text(encoding="utf-8")
    original_content = content
    changes = []

    # Step 1: Add import
    content, imported = add_logging_import(content, str(file_path))
    if imported:
        changes.append("added_import")

    # Step 2: Replace prints (commented out - too risky for auto)
    # content, n_prints = replace_prints_with_logging(content)
    # if n_prints > 0:
    #     changes.append(f"replaced_{n_prints}_prints")

    if content != original_content:
        # Backup original
        backup_path = file_path.with_suffix(".py.bak")
        backup_path.write_text(original_content, encoding="utf-8")

        # Write updated
        file_path.write_text(content, encoding="utf-8")

        return {"status": "updated", "changes": changes, "backup": str(backup_path)}

    return {"status": "no_changes"}


def main():
    """Run the logging migration."""
    repo_root = Path(__file__).parent.parent

    print("=" * 70)
    print("STRUCTLOG MIGRATION - PHASE 1")
    print("=" * 70)
    print()

    for file_rel_path in PHASE1_FILES:
        file_path = repo_root / file_rel_path
        print(f"Processing: {file_rel_path}")

        result = process_file(file_path)

        if result["status"] == "updated":
            print(f"  ✓ Updated: {', '.join(result['changes'])}")
            print(f"  Backup: {result['backup']}")
        elif result["status"] == "skip":
            print(f"  ⊘ Skipped: {result['reason']}")
        else:
            print(f"  - No changes needed")
        print()

    print("=" * 70)
    print("PHASE 1 COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review changed files manually")
    print("2. Replace print() with proper log.info() calls with event names")
    print("3. Add log = get_logger(__name__).bind(...) in classes")
    print("4. Test with diagnostics script")
    print()


if __name__ == "__main__":
    main()
