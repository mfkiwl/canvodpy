#!/usr/bin/env python3
"""Comprehensive documentation analysis for canvod-readers package."""

import ast
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FunctionIssue:
    name: str
    line: int
    file: str
    issues: list[str]


@dataclass
class FileReport:
    filepath: str
    functions_without_docstrings: list[FunctionIssue]
    functions_without_return_hints: list[FunctionIssue]
    functions_with_missing_arg_hints: list[FunctionIssue]
    old_typing_imports: list[str]
    init_methods: list[dict]


def check_old_typing_syntax(source_code: str) -> list[str]:
    """Check for old typing module usage."""
    old_patterns = {
        "Optional": r"\bOptional\[",
        "Dict": r"\bDict\[",
        "List": r"\bList\[",
        "Tuple": r"\bTuple\[",
        "Set": r"\bSet\[",
        "Union": r"\bUnion\[",
    }

    found = []
    for name, pattern in old_patterns.items():
        if re.search(pattern, source_code):
            found.append(name)
    return found


def has_numpy_docstring(node: ast.FunctionDef) -> tuple[bool, list[str]]:
    """Check if function has proper NumPy-style docstring."""
    docstring = ast.get_docstring(node)
    if not docstring:
        return False, ["No docstring"]

    issues = []

    # Check for required sections in public functions
    if not node.name.startswith("_"):
        if (
            "Parameters" not in docstring and len(node.args.args) > 1
        ):  # More than just self
            issues.append("Missing 'Parameters' section")

        # Check for Returns section (unless __init__)
        if node.name not in ["__init__", "__post_init__"]:
            if "Returns" not in docstring and node.returns is not None:
                issues.append("Missing 'Returns' section")

    return len(issues) == 0, issues


def analyze_file(filepath: Path) -> FileReport:
    """Analyze a single Python file."""
    with open(filepath) as f:
        source = f.read()

    try:
        tree = ast.parse(source, str(filepath))
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return FileReport(str(filepath), [], [], [], [], [])

    functions_without_docstrings = []
    functions_without_return_hints = []
    functions_with_missing_arg_hints = []
    init_methods = []
    old_typing = check_old_typing_syntax(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            rel_path = filepath.relative_to(
                "/Users/work/Developer/GNSS/canvodpy/packages/canvod-readers"
            )

            # Check docstring
            has_doc, doc_issues = has_numpy_docstring(node)
            if not has_doc and not node.name.startswith(
                "_"
            ):  # Only report public functions
                functions_without_docstrings.append(
                    FunctionIssue(node.name, node.lineno, str(rel_path), doc_issues)
                )

            # Check return type hint
            if node.returns is None and node.name not in ["__init__", "__post_init__"]:
                if not node.name.startswith("_"):  # Only report public functions
                    functions_without_return_hints.append(
                        FunctionIssue(
                            node.name, node.lineno, str(rel_path), ["No return hint"]
                        )
                    )

            # Special handling for __init__ and __post_init__
            if node.name in ["__init__", "__post_init__"]:
                if node.returns is None:
                    functions_without_return_hints.append(
                        FunctionIssue(
                            node.name,
                            node.lineno,
                            str(rel_path),
                            ["Should have -> None"],
                        )
                    )

            # Check argument type hints
            missing_args = []
            for arg in node.args.args:
                if arg.annotation is None and arg.arg not in ["self", "cls"]:
                    missing_args.append(arg.arg)

            if missing_args and not node.name.startswith("_"):
                functions_with_missing_arg_hints.append(
                    FunctionIssue(node.name, node.lineno, str(rel_path), missing_args)
                )

            # Track __init__ and __post_init__
            if node.name in ["__init__", "__post_init__"]:
                parent_class = None
                for n in ast.walk(tree):
                    if isinstance(n, ast.ClassDef):
                        for item in n.body:
                            if item == node:
                                parent_class = n.name
                                break

                init_methods.append(
                    {
                        "class": parent_class or "Unknown",
                        "method": node.name,
                        "line": node.lineno,
                        "file": str(rel_path),
                        "has_docstring": bool(ast.get_docstring(node)),
                        "has_return_hint": node.returns is not None,
                        "missing_arg_hints": missing_args,
                    }
                )

    return FileReport(
        str(
            filepath.relative_to(
                "/Users/work/Developer/GNSS/canvodpy/packages/canvod-readers"
            )
        ),
        functions_without_docstrings,
        functions_without_return_hints,
        functions_with_missing_arg_hints,
        old_typing,
        init_methods,
    )


def main():
    """Run comprehensive analysis."""
    base_path = Path("/Users/work/Developer/GNSS/canvodpy/packages/canvod-readers")
    py_files = sorted(base_path.rglob("src/canvod/readers/**/*.py"))

    all_reports = []
    for py_file in py_files:
        report = analyze_file(py_file)
        all_reports.append(report)

    # Print comprehensive report
    print("=" * 80)
    print("CANVOD-READERS DOCUMENTATION ANALYSIS")
    print("=" * 80)

    # Summary statistics
    total_missing_docstrings = sum(
        len(r.functions_without_docstrings) for r in all_reports
    )
    total_missing_return_hints = sum(
        len(r.functions_without_return_hints) for r in all_reports
    )
    total_missing_arg_hints = sum(
        len(r.functions_with_missing_arg_hints) for r in all_reports
    )
    total_old_typing = sum(1 for r in all_reports if r.old_typing_imports)
    total_init_methods = sum(len(r.init_methods) for r in all_reports)

    print("\n📊 SUMMARY")
    print(f"  Total files analyzed: {len(all_reports)}")
    print(f"  Functions without docstrings: {total_missing_docstrings}")
    print(f"  Functions without return hints: {total_missing_return_hints}")
    print(f"  Functions with missing arg hints: {total_missing_arg_hints}")
    print(f"  Files with old typing syntax: {total_old_typing}")
    print(f"  __init__/__post_init__ methods: {total_init_methods}")

    # Detailed reports by category
    print("\n" + "=" * 80)
    print("1. FILES WITH OLD TYPING SYNTAX (NEEDS MODERNIZATION)")
    print("=" * 80)
    for report in all_reports:
        if report.old_typing_imports:
            print(f"\n📁 {report.filepath}")
            print(f"   Old imports found: {', '.join(report.old_typing_imports)}")

    print("\n" + "=" * 80)
    print("2. FUNCTIONS WITHOUT DOCSTRINGS")
    print("=" * 80)
    for report in all_reports:
        if report.functions_without_docstrings:
            print(f"\n📁 {report.filepath}")
            for func in report.functions_without_docstrings:
                print(f"   ❌ {func.name} (line {func.line}): {', '.join(func.issues)}")

    print("\n" + "=" * 80)
    print("3. FUNCTIONS WITHOUT RETURN TYPE HINTS")
    print("=" * 80)
    for report in all_reports:
        if report.functions_without_return_hints:
            print(f"\n📁 {report.filepath}")
            for func in report.functions_without_return_hints:
                print(f"   ⚠️  {func.name} (line {func.line})")

    print("\n" + "=" * 80)
    print("4. FUNCTIONS WITH MISSING ARGUMENT TYPE HINTS")
    print("=" * 80)
    for report in all_reports:
        if report.functions_with_missing_arg_hints:
            print(f"\n📁 {report.filepath}")
            for func in report.functions_with_missing_arg_hints:
                print(
                    f"   ⚠️  {func.name} (line {func.line}): missing hints for {', '.join(func.issues)}"
                )

    print("\n" + "=" * 80)
    print("5. __init__ AND __post_init__ METHODS AUDIT")
    print("=" * 80)
    for report in all_reports:
        if report.init_methods:
            print(f"\n📁 {report.filepath}")
            for method in report.init_methods:
                status = []
                if not method["has_return_hint"]:
                    status.append("❌ No -> None")
                if not method["has_docstring"]:
                    status.append("❌ No docstring")
                if method["missing_arg_hints"]:
                    status.append(
                        f"⚠️  Missing hints: {', '.join(method['missing_arg_hints'])}"
                    )

                status_str = "; ".join(status) if status else "✅ OK"
                print(
                    f"   {method['class']}.{method['method']} (line {method['line']}): {status_str}"
                )

    # Priority recommendations
    print("\n" + "=" * 80)
    print("🎯 PRIORITY RECOMMENDATIONS")
    print("=" * 80)

    if total_old_typing > 0:
        print(f"\n1. MODERNIZE TYPING (HIGH PRIORITY - {total_old_typing} files)")
        print("   Replace: Optional[X] → X | None")
        print("   Replace: Dict[X, Y] → dict[X, Y]")
        print("   Replace: List[X] → list[X]")

    if total_missing_return_hints > 0:
        print(
            f"\n2. ADD RETURN TYPE HINTS (HIGH PRIORITY - {total_missing_return_hints} functions)"
        )
        print("   All functions need explicit return types")
        print("   __init__/__post_init__ need -> None")

    if total_missing_docstrings > 0:
        print(
            f"\n3. ADD DOCSTRINGS (MEDIUM PRIORITY - {total_missing_docstrings} functions)"
        )
        print("   Use NumPy style with Parameters/Returns/Raises sections")

    if total_missing_arg_hints > 0:
        print(
            f"\n4. COMPLETE ARGUMENT TYPE HINTS (MEDIUM PRIORITY - {total_missing_arg_hints} functions)"
        )
        print("   All arguments except self/cls need type hints")


if __name__ == "__main__":
    main()
