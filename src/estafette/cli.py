"""The estafette command-line interface.

In init-core-v1 the ``assess`` command loads and validates the transfer
manifest and prints an honest summary. It runs no checks and emits no tier
verdict (invariant I1): the output is explicitly labelled not-yet-implemented.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from estafette import __version__
from estafette.manifest import (
    ManifestError,
    TransferManifest,
    load_manifest,
    resolve_manifest_path,
)

_MANIFEST_HELP = "Transfer manifest path (default: <target>/transfer.yaml)."

app = typer.Typer(
    add_completion=False,
    help="Mechanically assess whether a proof of concept is transferable.",
)


@app.callback()
def main() -> None:
    """estafette — is this proof of concept transferable?"""
    # Presence of a callback keeps 'assess' as an explicit subcommand.


def _print_summary(target: str, manifest_path: Path, manifest: TransferManifest) -> None:
    typer.echo(f"estafette {__version__}")
    typer.echo(f"target:   {target}")
    typer.echo(f"manifest: {manifest_path}")
    typer.echo("")
    typer.echo("Transfer manifest (valid):")
    typer.echo(f"  name:    {manifest.name}")
    typer.echo(f"  licence: {manifest.licence}")
    typer.echo(f"  owner:   {manifest.owner}")
    typer.echo(f"  contact: {manifest.contact}")
    typer.echo(f"  status:  {manifest.status.value}")
    if manifest.deps:
        typer.echo(f"  deps:    {', '.join(manifest.deps)}")
    typer.echo("")
    typer.echo(
        "NOTE: checks and tier verdict are not yet implemented (init-core-v1). "
        "No verdict is produced."
    )


@app.command()
def assess(
    target: Annotated[str, typer.Argument(help="Path to a repository (or a git URL).")],
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", help=_MANIFEST_HELP),
    ] = None,
) -> None:
    """Load and validate the transfer manifest for TARGET."""
    manifest_path = resolve_manifest_path(target, manifest)
    try:
        loaded = load_manifest(manifest_path)
    except ManifestError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    _print_summary(target, manifest_path, loaded)


if __name__ == "__main__":  # pragma: no cover
    app()
