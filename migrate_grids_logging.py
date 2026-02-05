#!/usr/bin/env python3
"""
Migrate canvod-grids package from loguru to structlog.

Replaces all loguru logger usage with canvodpy.logging.get_logger().
"""

import re
from pathlib import Path

GRIDS_SRC = Path("/Users/work/Developer/GNSS/canvodpy/packages/canvod-grids/src")


def migrate_file(filepath: Path) -> tuple[bool, str]:
    """
    Migrate a single file from loguru to structlog.

    Returns
    -------
    changed : bool
        Whether the file was modified
    message : str
        Description of changes
    """
    content = filepath.read_text()
    original = content
    changes = []

    # 1. Replace import statement
    if "from loguru import logger" in content:
        content = content.replace(
            "from loguru import logger",
            "",  # Remove it, we'll add lazy import
        )
        changes.append("Removed loguru import")

        # Add lazy import function if not present
        if "_get_logger()" not in content:
            # Find the import section
            import_section_end = 0
            for i, line in enumerate(content.split("\n")):
                if line.strip() and not line.strip().startswith(("from ", "import ", '"""', "#")):
                    import_section_end = i
                    break

            lines = content.split("\n")
            lazy_import = [
                "",
                "",
                "def _get_logger():",
                '    """Lazy import to avoid circular dependency."""',
                "    from canvodpy.logging import get_logger",
                "",
                "    return get_logger(__name__)",
                "",
            ]
            lines = lines[:import_section_end] + lazy_import + lines[import_section_end:]
            content = "\n".join(lines)
            changes.append("Added lazy _get_logger()")

    # 2. Replace logger = logger assignments
    content = re.sub(
        r"(\s+)self\._logger = logger\b",
        r"\1self._logger = _get_logger()",
        content,
    )
    if "self._logger = _get_logger()" in content and "self._logger = logger" not in original:
        changes.append("Updated logger assignment")

    # 3. Convert f-string logging to structured logging
    # Pattern: logger.info(f"Some {variable} text")
    def convert_fstring_log(match):
        level = match.group(1)
        message = match.group(2)

        # Extract variables from f-string
        variables = re.findall(r"\{([^}]+)\}", message)

        # Create event name (first few words)
        plain_text = re.sub(r"\{[^}]+\}", "", message).strip()
        words = plain_text.split()[:3]
        event_name = "_".join(w.lower() for w in words if w.isalnum())

        if not variables:
            # No variables, simple message
            return f'{match.group(0).split("(")[0]}("{event_name}", message="{plain_text}")'

        # Build kwargs
        kwargs = []
        for var in variables:
            # Clean variable name
            clean_var = var.split(".")[0].split("[")[0]
            kwargs.append(f"{clean_var}={var}")

        kwargs_str = ", ".join(kwargs)
        return f'logger.{level}("{event_name}", {kwargs_str})'

    # Find patterns like: logger.info(f"...")
    content = re.sub(
        r'logger\.(\w+)\(f"([^"]+)"\)',
        convert_fstring_log,
        content,
    )

    if content != original:
        filepath.write_text(content)
        return True, f"✅ {filepath.name}: {', '.join(changes)}"
    return False, f"⏭️  {filepath.name}: No changes needed"


def main():
    """Migrate all Python files in canvod-grids."""
    print("=" * 60)
    print("Migrating canvod-grids from loguru to structlog")
    print("=" * 60)
    print()

    files = list(GRIDS_SRC.rglob("*.py"))
    print(f"Found {len(files)} Python files\n")

    modified = 0
    for filepath in sorted(files):
        changed, message = migrate_file(filepath)
        if changed:
            modified += 1
        print(message)

    print()
    print("=" * 60)
    print(f"✅ Migration complete: {modified}/{len(files)} files modified")
    print("=" * 60)


if __name__ == "__main__":
    main()
