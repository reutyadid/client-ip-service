import pytest

from ci_diagnosis.config import resolve_ai_api_key
from ci_diagnosis.github import BOT_LOGIN, is_our_comment
from ci_diagnosis.report import COMMENT_MARKER

GH_MODELS = "https://models.github.ai/inference"


def test_github_token_is_used_for_github_models():
    assert resolve_ai_api_key(GH_MODELS, "", "gh-token") == "gh-token"


def test_explicit_key_wins():
    assert resolve_ai_api_key("https://api.openai.com/v1", "sk-x", "gh") == "sk-x"


@pytest.mark.parametrize(
    "url",
    [
        "https://api.openai.com/v1",
        "http://ollama.local:11434/v1",
        "https://models.github.ai.evil.example/inference",  # lookalike host
    ],
)
def test_github_token_never_goes_to_another_provider(url):
    with pytest.raises(RuntimeError, match="AI_API_KEY is required"):
        resolve_ai_api_key(url, "", "gh-token")


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
