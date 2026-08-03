"""Core scaffolding logic for the Company OS template.

Kept CLI-free on purpose so it can be unit tested or reused (e.g. from a
future web/API frontend) without importing Typer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from importlib import resources
from pathlib import Path

TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
# Form-field placeholders kept in doc templates (filled per document, not at scaffold time)
IGNORE_LEFTOVER = {"{{TITLE}}", "{{NNNN}}"}
SKIP_NAMES = {"__pycache__", ".DS_Store"}
SKIP_SUFFIXES = {".pyc"}
TEMPLATE_README_NAME = "TEMPLATE_README.md"
TEMPLATE_PACKAGE = "company_os_cli"
TEMPLATE_RESOURCE = "template"


class ScaffoldError(RuntimeError):
    """Raised when scaffolding cannot proceed (bad args, unsafe target, ...)."""


@dataclass
class ScaffoldResult:
    dest: Path
    mapping: dict[str, str]
    leftover: list[str] = field(default_factory=list)


def slugify(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "company-os"


def build_vars(
    *,
    name: str,
    product: str,
    slug: str = "",
    llm_provider: str = "openrouter",
    model: str = "openrouter/free",
    langsmith_project: str = "",
) -> dict[str, str]:
    resolved_slug = slug or slugify(product)
    today = date.today()
    return {
        "COMPANY_NAME": name,
        "PRODUCT_NAME": product,
        "PRODUCT_SLUG": resolved_slug,
        "PROJECT_ID": f"proj-{resolved_slug}",
        "YEAR": str(today.year),
        "TODAY": today.isoformat(),
        "LLM_PROVIDER": llm_provider,
        "DEFAULT_MODEL": model,
        "LANGSMITH_PROJECT": langsmith_project or resolved_slug,
    }


def _should_copy(path: Path) -> bool:
    if path.name in SKIP_NAMES:
        return False
    if path.suffix in SKIP_SUFFIXES:
        return False
    return True


def _render(text: str, mapping: dict[str, str]) -> str:
    out = text
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def _copy_tree(src: Path, dest: Path, mapping: dict[str, str]) -> list[str]:
    leftover: list[str] = []
    for path in src.rglob("*"):
        if not _should_copy(path):
            continue
        rel = path.relative_to(src)
        parts = list(rel.parts)
        if parts and parts[-1] == TEMPLATE_README_NAME:
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
        rendered = _render(text, mapping)
        target.write_text(rendered, encoding="utf-8")
        leftover.extend(TOKEN_RE.findall(rendered))
    return sorted(set(leftover) - IGNORE_LEFTOVER)


def scaffold(
    *,
    name: str,
    product: str,
    out: str | Path,
    slug: str = "",
    force: bool = False,
    llm_provider: str = "openrouter",
    model: str = "openrouter/free",
    langsmith_project: str = "",
) -> ScaffoldResult:
    """Render the bundled Company OS template into ``out``.

    Raises:
        ScaffoldError: if ``out`` is a non-empty directory and ``force`` is False.
    """
    mapping = build_vars(
        name=name,
        product=product,
        slug=slug,
        llm_provider=llm_provider,
        model=model,
        langsmith_project=langsmith_project,
    )
    dest = Path(out).expanduser().resolve()

    if dest.exists() and any(dest.iterdir()) and not force:
        raise ScaffoldError(
            f"Refusing to write into non-empty directory: {dest} "
            "(pass force=True / --force to overwrite/merge)"
        )

    dest.mkdir(parents=True, exist_ok=True)

    template_ref = resources.files(TEMPLATE_PACKAGE) / TEMPLATE_RESOURCE
    with resources.as_file(template_ref) as template_path:
        leftover = _copy_tree(template_path, dest, mapping)

    starter = dest / "projects" / "_starter"
    renamed = dest / "projects" / mapping["PRODUCT_SLUG"]
    if starter.exists() and not renamed.exists():
        starter.rename(renamed)

    return ScaffoldResult(dest=dest, mapping=mapping, leftover=leftover)
