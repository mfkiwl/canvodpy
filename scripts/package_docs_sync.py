#!/usr/bin/env python3
"""Sync package docs and top-level docs into docs-site/ for Zensical builds."""

from __future__ import annotations

from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
DOCS_SITE = ROOT / "docs-site"

TOP_LEVEL_FILES = [
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
]

TOP_LEVEL_DOCS_DIR = ROOT / "docs"
TOP_LEVEL_DOCS_TARGET = DOCS_SITE / "docs"

API_DOCS_DIR = ROOT / "docs" / "api"
API_DOCS_TARGET = TOP_LEVEL_DOCS_TARGET / "api"

PACKAGES = [
    "canvod-readers",
    "canvod-aux",
    "canvod-store",
    "canvod-utils",
    "canvod-grids",
    "canvod-vod",
    "canvod-viz",
]

UMBRELLA = "canvodpy"


def _reset_docs_site() -> None:
    if DOCS_SITE.exists():
        shutil.rmtree(DOCS_SITE)
    DOCS_SITE.mkdir(parents=True, exist_ok=True)


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".md":
        content = src.read_text(encoding="utf-8")
        dest.write_text(_transform_markdown(content), encoding="utf-8")
    else:
        shutil.copy2(src, dest)


def _copy_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dest / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        _copy_file(path, target)


def _sync_top_level_docs() -> None:
    for src in TOP_LEVEL_FILES:
        if src.exists():
            _copy_file(src, DOCS_SITE / src.name)

    if TOP_LEVEL_DOCS_DIR.exists():
        _copy_tree(TOP_LEVEL_DOCS_DIR, TOP_LEVEL_DOCS_TARGET)

    if API_DOCS_DIR.exists():
        _copy_tree(API_DOCS_DIR, API_DOCS_TARGET)


def _sync_package_docs(package: str) -> None:
    package_root = ROOT / "packages" / package
    package_docs = package_root / "docs" / "source"
    package_assets = package_root / "docs" / "assets"
    package_readme = package_root / "README.md"
    target_root = DOCS_SITE / "packages" / package

    if package_readme.exists():
        _copy_file(package_readme, target_root / "README.md")

    if package_docs.exists():
        _copy_tree(package_docs, target_root)

    if package_assets.exists():
        _copy_tree(package_assets, target_root / "assets")


def _sync_umbrella_docs() -> None:
    umbrella_root = ROOT / UMBRELLA
    umbrella_readme = umbrella_root / "README.md"
    target_root = DOCS_SITE / UMBRELLA
    if umbrella_readme.exists():
        _copy_file(umbrella_readme, target_root / "README.md")


DOCS_SITE_NOTICE = """\
This directory is a generated, tracked mirror of documentation sources.

Do not edit files here directly. Make changes in the original sources:
- Top-level docs: docs/
- Package docs: packages/<package>/docs/source/
- Package READMEs: packages/<package>/README.md

Use `just docs` or `just docs-build` to regenerate this directory.
"""


def _write_docs_site_notice() -> None:
    notice = DOCS_SITE / "GENERATED.md"
    notice.write_text(DOCS_SITE_NOTICE, encoding="utf-8")


def _normalize_doc_link(link: str) -> str:
    if link.startswith(("http://", "https://", "/")):
        return link
    if link.endswith((".md", ".html")):
        return link
    if "#" in link:
        base, anchor = link.split("#", 1)
        base = base or link
        return f"{base}.md#{anchor}"
    return f"{link}.md"


def _parse_grid_card(lines: list[str], start: int) -> tuple[list[str], int]:
    line = lines[start]
    title = line.split("}", 1)[1].strip() if "}" in line else line.strip()
    body: list[str] = []
    link: str | None = None
    i = start + 1
    while i < len(lines):
        current = lines[i].rstrip()
        stripped = current.strip()
        if stripped.startswith(":link:"):
            link = stripped.split(":", 2)[2].strip()
            i += 1
            continue
        if stripped.startswith(":link-type:"):
            i += 1
            continue
        if stripped == ":::":  # end card
            i += 1
            break
        body.append(current)
        i += 1
    output: list[str] = [f"### {title}"]
    if link:
        output.append(f"Link: [{link}]({_normalize_doc_link(link)})")
    if body:
        output.extend(body)
    return output, i


def _parse_tab_item(lines: list[str], start: int) -> tuple[list[str], int]:
    line = lines[start]
    title = line.split("}", 1)[1].strip() if "}" in line else line.strip()
    body: list[str] = []
    i = start + 1
    while i < len(lines):
        current = lines[i].rstrip()
        if current.strip() == ":::":  # end tab
            i += 1
            break
        body.append(current)
        i += 1
    output: list[str] = [f"### {title}"]
    if body:
        output.extend(body)
    return output, i


def _parse_fenced_block(lines: list[str], start: int) -> tuple[list[str], int]:
    content: list[str] = []
    i = start + 1
    while i < len(lines):
        current = lines[i].rstrip()
        if current.strip() == "```":
            i += 1
            break
        content.append(current)
        i += 1
    return content, i


def _transform_markdown(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    in_grid = False
    in_tabset = False
    in_code_fence = False
    in_callout = False

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if stripped.startswith("> [!") and stripped.endswith("]"):
            label = stripped[4:-1].strip().lower()
            out.append(f"!!! {label}")
            in_callout = True
            i += 1
            continue

        if in_callout:
            if stripped == ">":
                out.append("")
                i += 1
                continue
            if stripped.startswith("> "):
                out.append(f"    {stripped[2:]}")
                i += 1
                continue
            if stripped == "":
                out.append("")
                i += 1
                continue
            in_callout = False

        if stripped == "```{toctree}":
            _, i = _parse_fenced_block(lines, i)
            continue

        if stripped == "```{eval-rst}":
            content, i = _parse_fenced_block(lines, i)
            slug: str | None = None
            for entry in content:
                match = re.search(r"(?<=\s)canvod-[a-z-]+(?=\s)", entry)
                if match:
                    slug = match.group(0)
                    break
            if slug:
                out.append(
                    f"> See the unified API reference: "
                    f"[{slug}](../../docs/api/{slug}.md)"
                )
            else:
                out.append(
                    "> See the unified API reference: "
                    "[API Reference](../../docs/api/)"
                )
            out.append("")
            continue

        if stripped.startswith("```"):
            if stripped.startswith("```{") and stripped.endswith("}"):
                lang = stripped[4:-1].strip()
                out.append(f"```{lang}")
                in_code_fence = True
                i += 1
                continue
            if stripped.startswith("```{code-block}"):
                lang = stripped[len("```{code-block}"):].strip()
                out.append(f"```{lang}")
                in_code_fence = True
                i += 1
                continue
            if stripped == "```":
                out.append(line)
                in_code_fence = False
                i += 1
                continue

        if stripped.startswith("::::{grid"):
            in_grid = True
            i += 1
            continue

        if in_grid and stripped == "::::":
            in_grid = False
            i += 1
            continue

        if in_grid and stripped.startswith(":::{grid-item-card}"):
            block, i = _parse_grid_card(lines, i)
            out.extend(block)
            continue

        if stripped.startswith("::::{tab-set"):
            in_tabset = True
            i += 1
            continue

        if in_tabset and stripped == "::::":
            in_tabset = False
            i += 1
            continue

        if in_tabset and stripped.startswith(":::{tab-item}"):
            block, i = _parse_tab_item(lines, i)
            out.extend(block)
            continue

        if in_grid and stripped.startswith(":gutter:"):
            i += 1
            continue

        out.append(line)
        i += 1

    return "\n".join(out) + "\n"


def main() -> None:
    _reset_docs_site()
    _sync_top_level_docs()
    for package in PACKAGES:
        _sync_package_docs(package)
    _sync_umbrella_docs()
    _write_docs_site_notice()


if __name__ == "__main__":
    main()
