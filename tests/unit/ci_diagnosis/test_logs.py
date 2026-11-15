import pytest

from ci_diagnosis.logs import excerpt, redact, strip_timestamps


@pytest.mark.parametrize(
    ("secret", "label"),
    [
        ("ghp_" + "a" * 36, "classic GitHub token"),
        ("ghs_" + "B" * 36, "GitHub Actions token"),
        ("github_pat_" + "c" * 40, "fine-grained GitHub token"),
        ("dckr_pat_" + "d" * 27, "Docker Hub token"),
        ("AKIA" + "E" * 16, "AWS access key id"),
        ("eyJhbGciOiJIUzI1.eyJzdWIiOiIxMjM0.SflKxwRJSMeKKF2QT4", "JWT"),
    ],
)
def test_known_token_formats_are_redacted(secret, label):
    assert secret not in redact(f"value: {secret} end"), label


def test_private_key_block_is_redacted():
    key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEow\nabc\n-----END RSA PRIVATE KEY-----"
    assert "MIIEow" not in redact(f"before\n{key}\nafter")


def test_secret_looking_assignments_keep_the_name():
    out = redact(
        "DB_PASSWORD=hunter2 api_key: s3cr3t Authorization: Bearer abcdefghijklmnop1234"
    )
    assert (
        "hunter2" not in out and "s3cr3t" not in out and "abcdefghijklmnop" not in out
    )
    assert "DB_PASSWORD=[REDACTED]" in out


def test_ordinary_log_lines_are_unchanged():
    line = "FAILED tests/test_app.py::test_root - assert 500 == 200"
    assert redact(line) == line


def test_timestamps_are_removed():
    assert strip_timestamps("2026-11-15T12:00:00.1234567Z hello") == ["hello"]


def test_excerpt_keeps_error_context_and_tail():
    log = "\n".join(
        [f"noise {i}" for i in range(100)]
        + ["##[error]Process completed with exit code 1."]
        + [f"later {i}" for i in range(100)]
    )
    out = excerpt(log, max_chars=10_000, context=2, tail=5)
    assert "##[error]Process completed with exit code 1." in out
    assert "noise 99" in out  # context before the error
    assert "later 99" in out  # tail
    assert "noise 10" not in out  # unrelated noise dropped
    assert "[...]" in out


def test_excerpt_respects_max_chars_and_keeps_the_end():
    log = "\n".join(f"error line {i}" for i in range(1000))
    out = excerpt(log, max_chars=500)
    assert len(out) <= 500
    assert out.endswith("error line 999")


def test_excerpt_redacts_secrets():
    log = "##[error]login failed with token ghp_" + "x" * 36
    assert "ghp_" not in excerpt(log, max_chars=1000)


def test_private_key_cut_by_the_excerpt_is_still_redacted():
    # The error is right after BEGIN; the excerpt keeps BEGIN and part of the
    # body but not END, which used to defeat the PEM pattern.
    body = [f"KEYMATERIAL{i:03d}" for i in range(60)]
    log = "\n".join(
        ["-----BEGIN RSA PRIVATE KEY-----", "##[error]oops", *body]
        + ["-----END RSA PRIVATE KEY-----"]
        + [f"filler {i}" for i in range(200)]
    )
    out = excerpt(log, max_chars=10_000, context=8, tail=5)
    assert "KEYMATERIAL" not in out


def test_error_windows_survive_a_long_tail():
    # The cause is far above a long tail; the old single budget cut it off.
    log = "\n".join(
        ["setup"] * 50
        + ["ModuleNotFoundError: No module named 'fastapi'"]
        + ["noise"] * 50
        + [f"tail line {i} " + "x" * 60 for i in range(40)]
    )
    out = excerpt(log, max_chars=1000)
    assert "ModuleNotFoundError" in out
    assert "tail line 39" in out
    assert len(out) <= 1000
