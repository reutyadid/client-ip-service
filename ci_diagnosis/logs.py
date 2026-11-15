"""Turn raw job logs into a short, secret-free excerpt for the model."""

import re

# Every GitHub Actions log line starts with an ISO timestamp.
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z ?")

# Lines that usually mark the cause of a failure.
_ERROR_HINT = re.compile(
    r"##\[error\]|[a-z]*error\b|\bfailed\b|\bfailure\b|exception|traceback|"
    r"assert|fatal|denied|not found|timed out|exit code [1-9]",
    re.IGNORECASE,
)

# Best-effort secret patterns, on top of GitHub's own masking of registered
# secrets. Defense in depth, not a boundary: the real boundary is that the
# diagnosis job holds no secret worth leaking. Each entry is (pattern, replacement).
_SECRET_PATTERNS = [
    # Private keys (PEM blocks)
    (
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        "[REDACTED]",
    ),
    # GitHub tokens: ghp_, gho_, ghu_, ghs_, ghr_, github_pat_
    (
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
        "[REDACTED]",
    ),
    # Docker Hub personal access tokens
    (re.compile(r"\bdckr_pat_[A-Za-z0-9_-]{20,}\b"), "[REDACTED]"),
    # AWS access key IDs
    (re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"), "[REDACTED]"),
    # JWTs (three base64url parts)
    (
        re.compile(
            r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"
        ),
        "[REDACTED]",
    ),
    # Bearer tokens in headers: keep "Bearer "
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]{16,}=*"), r"\1[REDACTED]"),
    # key=value / key: value for secret-looking names: keep the name
    (
        re.compile(
            r"(?i)\b([A-Za-z0-9_]*(?:password|passwd|secret|token|api[_-]?key)"
            r"[A-Za-z0-9_]*\s*[=:]\s*)\S+"
        ),
        r"\1[REDACTED]",
    ),
]


def redact(text: str) -> str:
    """Replace anything that looks like a secret with [REDACTED]."""
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def strip_timestamps(log: str) -> list[str]:
    return [_TIMESTAMP.sub("", line) for line in log.splitlines()]


_TRUNCATED = "[...truncated...]"


def _join(lines: list[str], indexes: list[int]) -> str:
    """Join the chosen lines, marking every gap with [...]."""
    out: list[str] = []
    previous = -2
    for i in indexes:
        if i != previous + 1:
            out.append("[...]")
        out.append(lines[i])
        previous = i
    return "\n".join(out)


def excerpt(log: str, max_chars: int, context: int = 8, tail: int = 40) -> str:
    """The lines around errors plus the end of the log, within max_chars.

    Half the budget goes to the error windows, from the first error on (the
    cause often appears before the final failure message), and half to the
    tail, where the failure is reported. A separate budget for each keeps the
    tail from crowding out the windows.
    """
    # Redact the whole log first: a secret that spans lines (a PEM key) is
    # only recognizable before the selection cuts it apart.
    lines = strip_timestamps(redact(log))
    tail_start = max(0, len(lines) - tail)
    windows: set[int] = set()
    for i, line in enumerate(lines[:tail_start]):
        if _ERROR_HINT.search(line):
            windows.update(range(max(0, i - context), min(tail_start, i + context + 1)))

    # Budgets include the truncation markers, so the result never exceeds
    # max_chars.
    tail_budget = max_chars // 2 if windows else max_chars
    tail_text = _join(lines, list(range(tail_start, len(lines))))
    if len(tail_text) > tail_budget:
        keep = max(0, tail_budget - len(_TRUNCATED) - 1)
        tail_text = f"{_TRUNCATED}\n{tail_text[-keep:] if keep else ''}"
    if not windows:
        return tail_text
    windows_budget = max_chars - len(tail_text) - 1  # 1 for the joining newline
    windows_text = _join(lines, sorted(windows))
    if len(windows_text) > windows_budget:
        keep = max(0, windows_budget - len(_TRUNCATED) - 1)
        windows_text = f"{windows_text[:keep]}\n{_TRUNCATED}"
    return f"{windows_text}\n{tail_text}"
