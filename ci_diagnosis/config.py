"""Configuration from environment variables set by the workflow. No defaults
in code: the workflow passes every value, so a missing one fails fast. The one
exception is AI_API_KEY: secrets are not passed to pull requests from forks,
and without it the job still posts a plain failure notice."""

import os
from dataclasses import dataclass


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable {name}")
    return value


@dataclass(frozen=True)
class Config:
    github_token: str
    github_api_url: str
    repository: str
    run_id: str
    own_job_name: str
    pr_number: int | None
    step_summary_path: str
    ai_base_url: str
    ai_model: str
    ai_api_key: str  # empty when the secret is not available
    run_url: str


def load_config() -> Config:
    token = _require("GITHUB_TOKEN")
    repository = _require("GITHUB_REPOSITORY")
    run_id = _require("GITHUB_RUN_ID")
    pr = os.environ.get("PR_NUMBER", "").strip()
    return Config(
        github_token=token,
        github_api_url=_require("GITHUB_API_URL"),
        repository=repository,
        run_id=run_id,
        own_job_name=_require("OWN_JOB_NAME"),
        pr_number=int(pr) if pr else None,
        step_summary_path=_require("GITHUB_STEP_SUMMARY"),
        ai_base_url=_require("AI_API_BASE_URL"),
        ai_model=_require("AI_MODEL"),
        ai_api_key=os.environ.get("AI_API_KEY", "").strip(),
        run_url=f"{_require('GITHUB_SERVER_URL')}/{repository}/actions/runs/{run_id}",
    )
