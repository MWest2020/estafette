"""Render the report database (reports/) into a deterministic static site.

`reports/` is the datastore; this is a pure view over it — no server, no
database engine, no web framework (invariant I2). Output is byte-identical for
the same reports (invariant I5): no timestamps, no absolute paths.
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

from estafette.report import TransferabilityReport

_CSS = """
body { font-family: system-ui, sans-serif; max-width: 60rem; margin: 2rem auto; }
body { padding: 0 1rem; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #ddd; }
.badge { padding: 0.1rem 0.5rem; border-radius: 0.5rem; font-size: 0.85rem; }
.pass { background: #cd7f32; color: #fff; }
.fail { background: #eee; color: #555; }
code { background: #f4f4f4; padding: 0 0.3rem; }
""".strip()


def _slug(name: str, commit: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "report"
    return f"{base}-{commit[:12]}"


def _page(title: str, body: str) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{escape(title)}</title>\n<style>{_CSS}</style>\n</head>\n<body>\n"
        f"{body}\n</body>\n</html>\n"
    )


def load_reports(reports_dir: Path) -> list[TransferabilityReport]:
    """Load every report.json under ``reports_dir``, skipping unparseable ones."""
    reports: list[TransferabilityReport] = []
    if not reports_dir.is_dir():
        return reports
    for path in sorted(reports_dir.glob("*/report.json")):
        try:
            reports.append(TransferabilityReport.model_validate_json(path.read_text("utf-8")))
        except (ValueError, OSError):
            continue
    return sorted(reports, key=lambda r: (r.manifest.get("name", ""), r.commit))


def _badge(passed: bool) -> str:
    cls, label = ("pass", "bronze") if passed else ("fail", "not bronze")
    return f'<span class="badge {cls}">{label}</span>'


def render_index(reports: list[TransferabilityReport]) -> str:
    if not reports:
        return _page("estafette catalogue", "<h1>estafette catalogue</h1>\n<p>No reports yet.</p>")
    rows = []
    for report in reports:
        name = escape(report.manifest.get("name", "?"))
        gaps = sum(len(c.gaps) for c in report.checks)
        href = escape(_slug(report.manifest.get("name", "report"), report.commit) + ".html")
        rows.append(
            f"<tr><td><a href=\"{href}\">{name}</a></td>"
            f"<td>{_badge(report.bronze)}</td>"
            f"<td><code>{escape(report.commit[:12])}</code></td>"
            f"<td>{gaps}</td></tr>"
        )
    table = (
        "<table>\n<tr><th>PoC</th><th>Verdict</th><th>Commit</th><th>Gaps</th></tr>\n"
        + "\n".join(rows)
        + "\n</table>"
    )
    body = f"<h1>estafette catalogue</h1>\n<p>{len(reports)} assessed project(s).</p>\n{table}"
    return _page("estafette catalogue", body)


def render_detail(report: TransferabilityReport) -> str:
    name = escape(report.manifest.get("name", "?"))
    lines = [
        f"<h1>{name} — {_badge(report.bronze)}</h1>",
        f"<p>Commit <code>{escape(report.commit)}</code> · "
        f"estafette {escape(report.estafette_version)} "
        f"(tier doc v{escape(report.tier_doc_version)})</p>",
        "<h2>Bronze criteria</h2>\n<ul>",
    ]
    for c in report.criteria:
        mark = "✓" if c.passed else "✗"
        lines.append(f"<li>{mark} {escape(c.id)} {escape(c.title)}</li>")
    lines.append("</ul>\n<h2>Checks</h2>")
    for check in report.checks:
        lines.append(f"<h3>{escape(check.name)}: {escape(check.status)}</h3>")
        if check.gaps:
            lines.append("<ul>")
            for gap in check.gaps:
                lines.append(
                    f"<li>{escape(gap.message)}<br><em>fix:</em> {escape(gap.remediation)}</li>"
                )
            lines.append("</ul>")
    sp = report.silver_preview
    lines.append("<h2>Silver preview (informational)</h2>")
    if not sp.available:
        lines.append(f"<p>not assessable — {escape(sp.reason or '')}</p>")
    elif sp.would_pass:
        lines.append("<p>would pass silver: yes</p>")
    else:
        lines.append(f"<p>would pass silver: no ({escape(sp.classification or '')})</p>")
    lines.append('<p><a href="index.html">&larr; back</a></p>')
    return _page(f"{report.manifest.get('name', 'report')} — estafette", "\n".join(lines))


def generate_site(reports_dir: Path, out_dir: Path) -> tuple[int, Path]:
    """Render the catalogue to ``out_dir``; return (report count, index path)."""
    reports = load_reports(reports_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for report in reports:
        fname = _slug(report.manifest.get("name", "report"), report.commit) + ".html"
        (out_dir / fname).write_text(render_detail(report), encoding="utf-8")
    index = out_dir / "index.html"
    index.write_text(render_index(reports), encoding="utf-8")
    return len(reports), index
