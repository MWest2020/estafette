"""Render the PoC catalogue (catalog/) into a deterministic static site.

Entries are the unit; the verdict is an optional badge on entries that reference
an estafette assessment. Pure view — no server, no database engine, no web
framework (I2). Output is byte-identical for the same inputs (I5): no timestamps,
no absolute paths.
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

from estafette.entry import PoCEntry, load_entries
from estafette.report import TransferabilityReport

_CSS = """
body { font-family: system-ui, sans-serif; max-width: 60rem; margin: 2rem auto; }
body { padding: 0 1rem; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #ddd; }
.badge { padding: 0.1rem 0.5rem; border-radius: 0.5rem; font-size: 0.85rem; }
.pass { background: #cd7f32; color: #fff; }
.na { background: #eee; color: #555; }
.concl { color: #333; }
code { background: #f4f4f4; padding: 0 0.3rem; }
""".strip()


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "entry"


def _page(title: str, body: str) -> str:
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{escape(title)}</title>\n<style>{_CSS}</style>\n</head>\n<body>\n"
        f"{body}\n</body>\n</html>\n"
    )


def _load_assessment(entry: PoCEntry, base: Path) -> TransferabilityReport | None:
    if not entry.assessment:
        return None
    try:
        return TransferabilityReport.model_validate_json(
            (base / entry.assessment).read_text(encoding="utf-8")
        )
    except (ValueError, OSError):
        return None


def _verdict_badge(report: TransferabilityReport | None) -> str:
    if report is None:
        return '<span class="badge na">no verdict</span>'
    label = "bronze" if report.bronze else "not bronze"
    return f'<span class="badge pass">{label}</span>'


def _snippet(text: str, limit: int = 120) -> str:
    text = " ".join(text.split())
    return escape(text if len(text) <= limit else text[:limit].rstrip() + "…")


def render_index(pairs: list[tuple[PoCEntry, TransferabilityReport | None]]) -> str:
    if not pairs:
        return _page("PoC catalogue", "<h1>PoC catalogue</h1>\n<p>No entries yet.</p>")
    rows = []
    for entry, report in pairs:
        href = escape(_slug(entry.name) + ".html")
        rows.append(
            f'<tr><td><a href="{href}">{escape(entry.name)}</a></td>'
            f"<td>{escape(entry.kind.value)}</td>"
            f"<td>{escape(entry.status.value)}</td>"
            f"<td>{_verdict_badge(report) if entry.assessment else ''}</td>"
            f'<td class="concl">{_snippet(entry.conclusion)}</td></tr>'
        )
    table = (
        "<table>\n<tr><th>PoC</th><th>Kind</th><th>Status</th>"
        "<th>Verdict</th><th>Conclusion</th></tr>\n" + "\n".join(rows) + "\n</table>"
    )
    body = f"<h1>PoC catalogue</h1>\n<p>{len(pairs)} proof(s) of concept.</p>\n{table}"
    return _page("PoC catalogue", body)


def _links(entry: PoCEntry) -> str:
    items = []
    for label, url in (("repo", entry.repo), ("doc", entry.doc),
                       ("demo", entry.demo), ("publiccode", entry.publiccode)):
        if url:
            items.append(f'<li>{label}: <code>{escape(url)}</code></li>')
    return "<ul>\n" + "\n".join(items) + "\n</ul>" if items else ""


def render_detail(entry: PoCEntry, report: TransferabilityReport | None) -> str:
    badge = _verdict_badge(report) if entry.assessment else ""
    lines = [
        f"<h1>{escape(entry.name)} {badge}</h1>",
        f"<p>{escape(entry.kind.value)} · {escape(entry.status.value)} · "
        f"owner {escape(entry.owner)} · {escape(entry.contact)}</p>",
        "<h2>Conclusion</h2>",
        f'<p class="concl">{escape(entry.conclusion)}</p>',
    ]
    links = _links(entry)
    if links:
        lines += ["<h2>Links</h2>", links]
    if report is not None:
        lines.append("<h2>Transferability assessment</h2>\n<ul>")
        for c in report.criteria:
            lines.append(f"<li>{'✓' if c.passed else '✗'} {escape(c.id)} {escape(c.title)}</li>")
        lines.append("</ul>")
    lines.append('<p><a href="index.html">&larr; back</a></p>')
    return _page(f"{entry.name} — PoC catalogue", "\n".join(lines))


def generate_site(catalog_dir: Path, out_dir: Path, base: Path | None = None) -> tuple[int, Path]:
    """Render the catalogue to ``out_dir``; return (entry count, index path)."""
    base = base if base is not None else Path(".")
    entries = load_entries(catalog_dir)
    pairs = [(e, _load_assessment(e, base)) for e in entries]
    out_dir.mkdir(parents=True, exist_ok=True)
    for entry, report in pairs:
        (out_dir / (_slug(entry.name) + ".html")).write_text(
            render_detail(entry, report), encoding="utf-8"
        )
    index = out_dir / "index.html"
    index.write_text(render_index(pairs), encoding="utf-8")
    return len(pairs), index
