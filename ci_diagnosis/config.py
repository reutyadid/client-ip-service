"""Configuration from environment variables set by the workflow. No defaults
in code: the workflow passes every value, so a missing one fails fast."""

import os
from dataclasses import dataclass
from urllib.parse import urlparse

# The only provider that may receive the workflow's GITHUB_TOKEN as API key.
GITHUB_MODELS_HOST = "models.github.ai"


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable {name}")
    return value


@dataclass(frozen=True)
class Config:
    github_token: str
    github_api_url: str
    server_url: str
    repository: str
    run_id: str
    own_job_name: str
    pr_number: int | None
    step_summary_path: str
    ai_base_url: str
    ai_model: str
    ai_api_key: str

    @property
    def run_url(self) -> str:
        return f"{self.server_url}/{self.repository}/actions/runs/{self.run_id}"


def resolve_ai_api_key(base_url: str, ai_api_key: str, github_token: str) -> str:
    """The model API key. GITHUB_TOKEN is used only for GitHub Models: sending
    it to any other provider would hand a third party a token that can write
    to pull requests."""
    if ai_api_key:
        return ai_api_key
    if urlparse(base_url).hostname == GITHUB_MODELS_HOST:
        return github_token
    raise RuntimeError(
        f"AI_API_KEY is required for a provider other than {GITHUB_MODELS_HOST}"
    )


def load_config() -> Config:
    token = _require("GITHUB_TOKEN")
    base_url = _require("AI_API_BASE_URL")
    pr = os.environ.get("PR_NUMBER", "").strip()
    return Config(
        github_token=token,
        github_api_url=_require("GITHUB_API_URL"),
        server_url=_require("GITHUB_SERVER_URL"),
        repository=_require("GITHUB_REPOSITORY"),
        run_id=_require("GITHUB_RUN_ID"),
        own_job_name=_require("OWN_JOB_NAME"),
        pr_number=int(pr) if pr else None,
        step_summary_path=_require("GITHUB_STEP_SUMMARY"),
        ai_base_url=base_url,
        ai_model=_require("AI_MODEL"),
        ai_api_key=resolve_ai_api_key(
            base_url, os.environ.get("AI_API_KEY", "").strip(), token
        ),
    )
