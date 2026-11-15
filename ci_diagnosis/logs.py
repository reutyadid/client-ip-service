"""Turn raw job logs into a short, secret-free excerpt for the model."""

import re

# Every GitHub Actions log line starts with an ISO timestamp.
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z ?")

# Lines that usually mark the cause of a failure.
_ERROR_HINT = re.compile(
    r"##\[error\]|\berror\b|\bfailed\b|\bfailure\b|exception|traceback|"
    r"assert|fatal|denied|not found|timed out|exit code [1-9]",
    re.IGNORECASE,
)

# Best-effort secret patterns, on top of GitHub's own masking of known secrets.
_SECRET_PATTERNS = [
    # Private keys (PEM blocks)
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    # GitHub tokens: ghp_, gho_, ghu_, ghs_, ghr_, github_pat_
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    # Docker Hub personal access tokens
    re.compile(r"\bdckr_pat_[A-Za-z0-9_-]{20,}\b"),
    # AWS access key IDs
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    # JWTs (three base64url parts)
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    # Bearer tokens in headers
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]{16,}=*"),
    # key=value / key: value for secret-looking names
    re.compile(
        r"(?i)\b([A-Za-z0-9_]*(?:password|passwd|secret|token|api[_-]?key)"
        r"[A-Za-z0-9_]*\s*[=:]\s*)\S+"
    ),
]


def redact(text: str) -> str:
    """Replace anything that looks like a secret with [REDACTED]."""
    for pattern in _SECRET_PATTERNS:
        if pattern.groups:
            text = pattern.sub(lambda m: m.group(1) + "[REDACTED]", text)
        else:
            text = pattern.sub("[REDACTED]", text)
    return text


def strip_timestamps(log: str) -> list[str]:
    return [_TIMESTAMP.sub("", line) for line in log.splitlines()]


def excerpt(log: str, max_chars: int, context: int = 8, tail: int = 40) -> str:
    """Keep the lines around errors plus the end of the log, within max_chars.

    The end of a failed job's log usually holds the final error, and the
    error-hint windows catch causes that appear earlier.
    """
    # Redact the whole log first: a secret that spans lines (a PEM key) is
    # only recognizable before the selection cuts it apart.
    lines = strip_timestamps(redact(log))
    keep: set[int] = set(range(max(0, len(lines) - tail), len(lines)))
    for i, line in enumerate(lines):
        if _ERROR_HINT.search(line):
            keep.update(range(max(0, i - context), min(len(lines), i + context + 1)))

    selected: list[str] = []
    previous = -2
    for i in sorted(keep):
        if i != previous + 1:
            selected.append("[...]")
        selected.append(lines[i])
        previous = i

    text = "\n".join(selected)
    if len(text) > max_chars:
        # Keep the end: that is where the failure is reported.
        text = "[...truncated...]\n" + text[-max_chars:]
    return text
