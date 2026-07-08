from __future__ import annotations

from conftest import requires

from estafette.checks.protocol import CheckStatus
from estafette.checks.secrets import SecretsCheck

# A synthetic GitHub PAT: ghp_ + 36 chars. Not a real credential. Built at
# runtime (f-string over a variable) so the contiguous token is never baked as
# a constant into the compiled .pyc — where a scanner would otherwise find it.
_TOKEN_BODY = "0123456789abcdefghij0123456789abcdef"  # gitleaks:allow (synthetic test token)
FAKE_PAT = f"ghp_{_TOKEN_BODY}"


@requires("gitleaks")
def test_clean_repo_passes(repo):
    target = repo({"ok.py": "x = 1\n"})
    result = SecretsCheck().run(target)
    assert result.status is CheckStatus.passed
    assert result.gaps == []


@requires("gitleaks")
def test_planted_secret_detected_without_echoing_value(repo):
    target = repo({"leak.py": f'token = "{FAKE_PAT}"\n'})
    result = SecretsCheck().run(target)
    assert result.status is CheckStatus.failed
    assert result.gaps
    blob = " ".join(g.message + g.remediation for g in result.gaps)
    assert "leak.py" in blob
    assert FAKE_PAT not in blob  # location reported, secret value never echoed
