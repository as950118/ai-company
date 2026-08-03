#!/usr/bin/env python3
"""Scaffold a new Company OS project from this template kit."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent
SKIP_NAMES = {"scaffold.py", "__pycache__", ".DS_Store"}
SKIP_SUFFIXES = {".pyc"}

TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
# Form-field placeholders kept in doc templates (filled per document, not at scaffold time)
IGNORE_LEFTOVER = {"{{TITLE}}", "{{NNNN}}"}


def slugify(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "company-os"


def build_vars(args: argparse.Namespace) -> dict[str, str]:
    slug = args.slug or slugify(args.product)
    today = date.today()
    return {
        "COMPANY_NAME": args.name,
        "PRODUCT_NAME": args.product,
        "PRODUCT_SLUG": slug,
        "PROJECT_ID": f"proj-{slug}",
        "YEAR": str(today.year),
        "TODAY": today.isoformat(),
        "LLM_PROVIDER": args.llm_provider,
        "DEFAULT_MODEL": args.model,
        "LANGSMITH_PROJECT": args.langsmith_project or slug,
    }


def should_copy(path: Path) -> bool:
    if path.name in SKIP_NAMES:
        return False
    if path.suffix in SKIP_SUFFIXES:
        return False
    if path.name == "README.md" and path.parent == KIT_ROOT:
        # Kit README stays in the kit; skeleton gets TEMPLATE_README.md → README.md
        return False
    if path.name == "PLACEHOLDERS.md" and path.parent == KIT_ROOT:
        return False
    return True


def render(text: str, mapping: dict[str, str]) -> str:
    out = text
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def copy_tree(src: Path, dest: Path, mapping: dict[str, str]) -> list[str]:
    leftover: list[str] = []
    for path in src.rglob("*"):
        if not should_copy(path):
            continue
        rel = path.relative_to(src)
        # Rename kit-only starter readme
        parts = list(rel.parts)
        if parts and parts[-1] == "TEMPLATE_README.md":
            parts[-1] = "README.md"
            rel = Path(*parts)
        target = dest / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            target.write_bytes(raw)
            continue
        rendered = render(text, mapping)
        target.write_text(rendered, encoding="utf-8")
        leftover.extend(TOKEN_RE.findall(rendered))
    return sorted(set(leftover) - IGNORE_LEFTOVER)

def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Company OS from template")
    parser.add_argument("--name", required=True, help="Company display name")
    parser.add_argument("--product", required=True, help="Product name")
    parser.add_argument("--slug", default="", help="URL/path slug (default: from product)")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--force", action="store_true", help="Allow non-empty output dir")
    parser.add_argument("--llm-provider", default="openrouter")
    parser.add_argument("--model", default="openrouter/free")
    parser.add_argument("--langsmith-project", default="")
    args = parser.parse_args()

    mapping = build_vars(args)
    dest = Path(args.out).expanduser().resolve()

    if dest.exists() and any(dest.iterdir()) and not args.force:
        print(f"Refusing to write into non-empty directory: {dest}", file=sys.stderr)
        print("Pass --force to overwrite/merge.", file=sys.stderr)
        return 2

    dest.mkdir(parents=True, exist_ok=True)
    leftover = copy_tree(KIT_ROOT, dest, mapping)

    # Rename starter project folder to product slug when available
    starter = dest / "projects" / "_starter"
    renamed = dest / "projects" / mapping["PRODUCT_SLUG"]
    if starter.exists() and not renamed.exists():
        starter.rename(renamed)

    print("Scaffolded Company OS")
    print(f"  out:      {dest}")
    print(f"  company:  {mapping['COMPANY_NAME']}")
    print(f"  product:  {mapping['PRODUCT_NAME']}")
    print(f"  slug:     {mapping['PRODUCT_SLUG']}")
    if leftover:
        print("WARNING: unresolved placeholders:")
        for token in leftover:
            print(f"  - {token}")
        return 1
    print("Next:")
    print(f"  1. cd {dest}")
    print("  2. Review company/vision.md and roles/")
    print("  3. cp runtime/.env.example runtime/.env")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
