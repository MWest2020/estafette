"""Diagnostic classification of harness failures (pure, no podman).

Maps captured build/run logs to exactly one category. Being a pure function of
the logs, it is fully unit-testable without podman, and because it feeds only an
informational silver preview, a misclassification is low-stakes (invariant I3:
every outcome still yields an actionable gap, and `other` keeps a log tail).
"""

from __future__ import annotations

import re
from enum import StrEnum


class Category(StrEnum):
    missing_declared_dep = "missing-declared-dep"
    undeclared_system_dep = "undeclared-system-dep"
    unreachable_internal_service = "unreachable-internal-service"
    requires_unavailable_data = "requires-unavailable-data"
    other = "other"


# Ordered: the first category with a matching pattern wins. Order is deliberate
# — network and application-dependency signals are checked before the broad
# "file not found" signals that would otherwise swallow them.
_PATTERNS: list[tuple[Category, list[str]]] = [
    (
        Category.missing_declared_dep,
        [
            r"ModuleNotFoundError",
            r"No module named",
            r"Could not find a version that satisfies",
            r"Cannot find module",
            r"npm ERR!.*404",
            r"package .* is not installed",
        ],
    ),
    (
        Category.undeclared_system_dep,
        [
            r"error while loading shared libraries",
            r"[\w.+-]+: command not found",
            r"fatal error: .*\.h: No such file",
            r"apt-get: not found",
            r"apk: not found",
            r"gcc: not found",
        ],
    ),
    (
        Category.unreachable_internal_service,
        [
            r"Connection refused",
            r"ECONNREFUSED",
            r"could not connect to server",
            r"Name or service not known",
            r"getaddrinfo",
            r"Temporary failure in name resolution",
        ],
    ),
    (
        Category.requires_unavailable_data,
        [
            r"FileNotFoundError",
            r"database .* does not exist",
            r"could not open file",
            r"No such file or directory",
        ],
    ),
]


def log_tail(text: str, lines: int = 20) -> str:
    """Return the last ``lines`` non-empty lines of ``text``."""
    kept = [line for line in text.splitlines() if line.strip()]
    return "\n".join(kept[-lines:])


def classify(build_log: str, run_log: str) -> Category:
    """Classify a harness failure from its combined logs."""
    combined = f"{build_log}\n{run_log}"
    for category, patterns in _PATTERNS:
        if any(re.search(p, combined) for p in patterns):
            return category
    return Category.other
