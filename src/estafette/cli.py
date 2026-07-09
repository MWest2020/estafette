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
from estafette.catalogue import generate_site
from estafette.checks.build import SilverPreview, preview_silver
from estafette.checks.protocol import CheckResult, CheckStatus
from estafette.checks.tooling import ToolNotFound
from estafette.manifest import (
    ManifestError,
    TransferManifest,
    load_manifest,
    resolve_manifest_path,
)
from estafette.report import build_report, capture_commit, write_report
from estafette.tier import compute_bronze

_MANIFEST_HELP = "Transfer manifest path (default: <target>/transfer.yaml)."
_REPORTS_HELP = "Directory reports accumulate in (default: reports/)."

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


def _print_silver(preview: SilverPreview) -> None:
    typer.echo("")
    typer.echo("Silver preview (informational — does not affect the verdict):")
    if not preview.available:
        typer.echo(f"  not assessable — {preview.reason}")
        return
    if preview.would_pass:
        typer.echo("  would pass silver: yes")
        return
    typer.echo(f"  would pass silver: no ({preview.classification})")
    for gap in preview.gaps:
        typer.echo(f"        - {gap.message}")
        typer.echo(f"          fix: {gap.remediation}")


@app.command()
def assess(
    target: Annotated[str, typer.Argument(help="Path to a repository (or a git URL).")],
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", help=_MANIFEST_HELP),
    ] = None,
    reports_dir: Annotated[
        Path,
        typer.Option("--reports-dir", help=_REPORTS_HELP),
    ] = Path("reports"),
) -> None:
    """Assess TARGET: run the checks, compute the bronze verdict, write the report."""
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

    preview = preview_silver(Path(target), loaded)
    _print_silver(preview)

    verdict = compute_bronze(results, loaded)
    commit = capture_commit(Path(target))
    report = build_report(Path(target), loaded, results, verdict, preview, __version__, commit)
    report_dir = write_report(reports_dir, report)

    typer.echo("")
    typer.secho(
        f"Bronze verdict: {'PASS' if verdict.passed else 'FAIL'}",
        fg=typer.colors.GREEN if verdict.passed else typer.colors.YELLOW,
    )
    typer.echo(f"Report written: {report_dir / 'report.md'}")


@app.command()
def catalogue(
    catalog: Annotated[
        Path, typer.Option("--catalog", help="Directory of PoC entry YAML files.")
    ] = Path("catalog"),
    out: Annotated[
        Path, typer.Option("--out", help="Output directory for the static site.")
    ] = Path("site"),
) -> None:
    """Render the PoC catalogue (entries) into a deterministic static site."""
    count, index = generate_site(catalog, out)
    typer.echo(f"Rendered {count} entr(y/ies) to {index}")


if __name__ == "__main__":  # pragma: no cover
    app()
