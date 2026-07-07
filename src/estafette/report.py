"""Transferability report: deterministic, append-only (invariant I5).

The body is built only from deterministic inputs (verdict, criteria, gaps, tool
versions, commit hash). Timings and absolute target paths are excluded, so the
same commit + estafette version yields a byte-identical body.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from pydantic import BaseModel

from estafette.checks.build import SilverPreview
from estafette.checks.protocol import CheckResult
from estafette.manifest import TransferManifest
from estafette.tier import BronzeVerdict

COMMIT_UNAVAILABLE = "unavailable"


class ReportGap(BaseModel):
    message: str
    remediation: str


class ReportCheck(BaseModel):
    name: str
    status: str
    gaps: list[ReportGap]


class ReportCriterion(BaseModel):
    id: str
    title: str
    passed: bool


class ReportSilver(BaseModel):
    available: bool
    would_pass: bool | None = None
    classification: str | None = None
    reason: str | None = None
    gaps: list[ReportGap] = []


class TransferabilityReport(BaseModel):
    estafette_version: str
    tier_doc_version: str
    commit: str
    manifest: dict[str, str]
    tool_versions: dict[str, str]
    bronze: bool
    criteria: list[ReportCriterion]
    checks: list[ReportCheck]
    silver_preview: ReportSilver


def capture_commit(target: Path) -> str:
    """Target commit hash, or COMMIT_UNAVAILABLE when it is not a git repo."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return COMMIT_UNAVAILABLE
    out = proc.stdout.strip()
    return out if proc.returncode == 0 and out else COMMIT_UNAVAILABLE


def _rel(text: str, root: str) -> str:
    return text.replace(root, ".")


def _gaps(gaps, root: str) -> list[ReportGap]:
    return [ReportGap(message=_rel(g.message, root), remediation=g.remediation) for g in gaps]


def _tool_versions(results: list[tuple[str, CheckResult]]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for _, result in results:
        tool = result.evidence.get("tool")
        if tool:
            versions[tool] = result.evidence.get("version", "unknown")
    return versions


def build_report(
    target: Path,
    manifest: TransferManifest,
    results: list[tuple[str, CheckResult]],
    verdict: BronzeVerdict,
    silver: SilverPreview,
    estafette_version: str,
    commit: str,
) -> TransferabilityReport:
    root = str(target)
    return TransferabilityReport(
        estafette_version=estafette_version,
        tier_doc_version=verdict.tier_doc_version,
        commit=commit,
        manifest={
            "name": manifest.name,
            "licence": manifest.licence,
            "owner": manifest.owner,
            "contact": manifest.contact,
            "status": manifest.status.value,
        },
        tool_versions=_tool_versions(results),
        bronze=verdict.passed,
        criteria=[
            ReportCriterion(id=c.id, title=c.title, passed=c.passed) for c in verdict.criteria
        ],
        checks=[
            ReportCheck(name=name, status=r.status.value, gaps=_gaps(r.gaps, root))
            for name, r in results
        ],
        silver_preview=ReportSilver(
            available=silver.available,
            would_pass=silver.would_pass,
            classification=silver.classification,
            reason=silver.reason,
            gaps=_gaps(silver.gaps, root),
        ),
    )


def render_json(report: TransferabilityReport) -> str:
    return json.dumps(report.model_dump(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(report: TransferabilityReport) -> str:
    verdict = "bronze" if report.bronze else "not bronze"
    lines = [
        f"# Transferability report: {report.manifest['name']}",
        "",
        f"- **Verdict:** {verdict}",
        f"- **Commit:** {report.commit}",
        f"- **estafette:** {report.estafette_version} (tier doc v{report.tier_doc_version})",
        "- **Tools:** " + ", ".join(f"{t}={v}" for t, v in sorted(report.tool_versions.items())),
        "",
        "## Bronze criteria",
        "",
    ]
    for c in report.criteria:
        lines.append(f"- [{'x' if c.passed else ' '}] {c.id} {c.title}")
    lines += ["", "## Checks and gaps", ""]
    for check in report.checks:
        lines.append(f"### {check.name}: {check.status}")
        for gap in check.gaps:
            lines.append(f"- {gap.message}")
            lines.append(f"  - fix: {gap.remediation}")
        lines.append("")
    lines += ["## Silver preview (informational)", ""]
    sp = report.silver_preview
    if not sp.available:
        lines.append(f"- not assessable — {sp.reason}")
    elif sp.would_pass:
        lines.append("- would pass silver: yes")
    else:
        lines.append(f"- would pass silver: no ({sp.classification})")
        for gap in sp.gaps:
            lines.append(f"  - {gap.message}")
    lines.append("")
    return "\n".join(lines)


def write_report(reports_dir: Path, report: TransferabilityReport) -> Path:
    """Write report.json + report.md append-only; return the directory used."""
    json_str, md_str = render_json(report), render_markdown(report)
    slug = report.commit[:12] if report.commit != COMMIT_UNAVAILABLE else COMMIT_UNAVAILABLE
    candidate = reports_dir / slug
    suffix = 1
    while candidate.exists():
        existing = candidate / "report.json"
        if existing.exists() and existing.read_text(encoding="utf-8") == json_str:
            return candidate  # identical → idempotent
        suffix += 1
        candidate = reports_dir / f"{slug}-{suffix}"
    candidate.mkdir(parents=True)
    (candidate / "report.json").write_text(json_str, encoding="utf-8")
    (candidate / "report.md").write_text(md_str, encoding="utf-8")
    return candidate
