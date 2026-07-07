from __future__ import annotations

from estafette.harness.classify import Category, classify, log_tail


def test_missing_declared_dep():
    assert classify("", "ModuleNotFoundError: No module named 'x'") is Category.missing_declared_dep
    assert classify("Could not find a version that satisfies foo", "") is (
        Category.missing_declared_dep
    )


def test_undeclared_system_dep():
    log = "./run.sh: line 3: psql: command not found"
    assert classify(log, "") is Category.undeclared_system_dep
    assert classify("error while loading shared libraries: libpq.so.5", "") is (
        Category.undeclared_system_dep
    )


def test_unreachable_internal_service():
    assert classify("", "psycopg2: Connection refused") is Category.unreachable_internal_service
    assert classify("", "getaddrinfo failed for db-host") is Category.unreachable_internal_service


def test_requires_unavailable_data():
    assert classify("", "FileNotFoundError: '/data/seed.csv'") is Category.requires_unavailable_data


def test_other_is_fallback():
    assert classify("everything is fine", "segfault at 0x0") is Category.other


def test_network_beats_broad_file_not_found():
    # A connection error and a "No such file" together -> network wins (ordered).
    log = "Connection refused\nNo such file or directory"
    assert classify("", log) is Category.unreachable_internal_service


def test_log_tail_keeps_last_nonempty_lines():
    text = "\n".join(str(i) for i in range(30))
    tail = log_tail(text, lines=5)
    assert tail.splitlines() == ["25", "26", "27", "28", "29"]
