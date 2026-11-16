from ci_diagnosis.github import BOT_LOGIN, is_our_comment
from ci_diagnosis.report import COMMENT_MARKER


def test_only_the_bots_marked_comment_is_ours():
    bot = {"user": {"login": BOT_LOGIN}, "body": f"{COMMENT_MARKER}\nreport"}
    quoted = {"user": {"login": "reviewer"}, "body": f"> {COMMENT_MARKER}\n> report"}
    unmarked = {"user": {"login": BOT_LOGIN}, "body": "another bot message"}
    assert is_our_comment(bot)
    assert not is_our_comment(quoted)
    assert not is_our_comment(unmarked)


def test_failed_jobs_includes_timeouts_and_cancelled_steps():
    import httpx2

    from ci_diagnosis.github import GitHubClient

    jobs = {
        "jobs": [
            {"id": 1, "name": "test", "conclusion": "success", "steps": []},
            {
                "id": 2,
                "name": "deploy",
                "conclusion": "timed_out",
                "steps": [
                    {"name": "Helm upgrade", "conclusion": "cancelled"},
                    {"name": "Collect diagnostics", "conclusion": "success"},
                ],
            },
            {"id": 3, "name": "ai-diagnosis", "conclusion": "failure", "steps": []},
        ]
    }
    transport = httpx2.MockTransport(lambda req: httpx2.Response(200, json=jobs))
    gh = GitHubClient("https://api.github.com", "t", "o/r", transport=transport)
    result = gh.failed_jobs("42", exclude="ai-diagnosis")
    assert [(j.name, j.failed_steps) for j in result] == [("deploy", ["Helm upgrade"])]
