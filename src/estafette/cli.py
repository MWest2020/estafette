"""The estafette command-line interface.

The ``assess`` command loads and validates the transfer manifest, runs the
static checks, and prints per-check results and gaps. It emits NO tier verdict
(invariant I1) — that arrives in tier-report-v1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from estafette import __version__
from estafette.assessment import build_checks, run_checks
from estafette.checks.protocol import CheckResult, CheckStatus
from estafette.checks.tooling import ToolNotFound
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


def _print_header(target: str, manifest_path: Path, manifest: TransferManifest) -> None:
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


def _print_result(name: str, result: CheckResult) -> None:
    mark = "PASS" if result.status is CheckStatus.passed else "FAIL"
    typer.echo(f"  [{mark}] {name}")
    for gap in result.gaps:
        typer.echo(f"        - {gap.message}")
        typer.echo(f"          fix: {gap.remediation}")


def _print_versions(results: list[tuple[str, CheckResult]]) -> None:
    versions = {}
    for _, result in results:
        tool = result.evidence.get("tool")
        if tool:
            versions[tool] = result.evidence.get("version", "unknown")
    if versions:
        typer.echo("")
        typer.echo("Tool versions: " + ", ".join(f"{t}={v}" for t, v in sorted(versions.items())))


@app.command()
def assess(
    target: Annotated[str, typer.Argument(help="Path to a repository (or a git URL).")],
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", help=_MANIFEST_HELP),
    ] = None,
) -> None:
    """Load the manifest for TARGET and run the static checks (no tier yet)."""
    manifest_path = resolve_manifest_path(target, manifest)
    try:
        loaded = load_manifest(manifest_path)
    except ManifestError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    _print_header(target, manifest_path, loaded)
    try:
        results = run_checks(build_checks(loaded, Path(target)), Path(target))
    except ToolNotFound as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo("")
    typer.echo("Static checks:")
    for name, result in results:
        _print_result(name, result)
    _print_versions(results)
    typer.echo("")
    typer.echo("NOTE: tier verdict is not yet implemented (tier-report-v1). No tier is produced.")


if __name__ == "__main__":  # pragma: no cover
    app()
