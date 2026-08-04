"""Typer CLI for company-os-cli.

Installed as the ``company-os`` console script (see pyproject.toml).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from . import __version__
from .scaffold import DEFAULT_EMBED_DIRNAME, ScaffoldError, scaffold

app = typer.Typer(
    name="company-os",
    help="Scaffold a Git-Markdown Multi-Agent Company OS (LangGraph/LangChain skeleton).",
    add_completion=False,
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"company-os-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the company-os-cli version and exit.",
    ),
) -> None:
    """Company OS CLI."""


@app.command()
def init(
    name: str = typer.Option(..., "--name", help="Company display name, e.g. 'Acme Agent Co'."),
    product: str = typer.Option(..., "--product", help="Product name, e.g. 'Acme Task Hub'."),
    out: Optional[Path] = typer.Option(
        None,
        "--out",
        help=(
            "Output directory for the new Company OS. "
            f"Defaults to ./{DEFAULT_EMBED_DIRNAME} in the current directory "
            "(handy when embedding into an existing repo without cluttering its root)."
        ),
    ),
    slug: str = typer.Option("", "--slug", help="URL/path slug (default: derived from --product)."),
    force: bool = typer.Option(
        False, "--force", help="Allow scaffolding into a non-empty directory (merge/overwrite)."
    ),
    llm_provider: str = typer.Option("openrouter", "--llm-provider", help="Default LLM provider."),
    model: str = typer.Option("openrouter/free", "--model", help="Default model id."),
    langsmith_project: str = typer.Option(
        "", "--langsmith-project", help="LangSmith project name (default: slug)."
    ),
) -> None:
    """Scaffold a new Company OS instance into OUT (default: ./.company-os)."""
    resolved_out = out if out is not None else Path.cwd() / DEFAULT_EMBED_DIRNAME
    try:
        result = scaffold(
            name=name,
            product=product,
            out=resolved_out,
            slug=slug,
            force=force,
            llm_provider=llm_provider,
            model=model,
            langsmith_project=langsmith_project,
        )
    except ScaffoldError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc

    typer.secho("Scaffolded Company OS", fg=typer.colors.GREEN, bold=True)
    typer.echo(f"  out:      {result.dest}")
    typer.echo(f"  company:  {result.mapping['COMPANY_NAME']}")
    typer.echo(f"  product:  {result.mapping['PRODUCT_NAME']}")
    typer.echo(f"  slug:     {result.mapping['PRODUCT_SLUG']}")

    if result.leftover:
        typer.secho("WARNING: unresolved placeholders:", fg=typer.colors.YELLOW, err=True)
        for token in result.leftover:
            typer.echo(f"  - {token}", err=True)
        raise typer.Exit(code=1)

    typer.echo("Next:")
    typer.echo(f"  1. cd {result.dest}")
    typer.echo("  2. Review company/vision.md and roles/")
    typer.echo("  3. cp runtime/.env.example runtime/.env")


if __name__ == "__main__":
    app()
