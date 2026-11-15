"""The GitHub REST API calls the diagnosis needs, and nothing more."""

from collections.abc import Iterator
from dataclasses import dataclass

import httpx2

from ci_diagnosis.report import COMMENT_MARKER

# Job and step results that count as "failed" for the diagnosis.
FAILED_JOB_CONCLUSIONS = {"failure", "timed_out"}
FAILED_STEP_CONCLUSIONS = {"failure", "timed_out", "cancelled"}

# The author of comments made with the workflow's GITHUB_TOKEN.
BOT_LOGIN = "github-actions[bot]"


@dataclass(frozen=True)
class FailedJob:
    id: int
    name: str
    failed_steps: list[str]


class GitHubClient:
    def __init__(
        self,
        api_url: str,
        token: str,
        repository: str,
        transport: httpx2.BaseTransport | None = None,
    ) -> None:
        self._repo = repository
        # httpx2 drops the Authorization header on cross-origin redirects; the
        # logs endpoint redirects to blob storage, which must not get the token.
        # `transport` lets tests replace the network, not the configuration.
        self._http = httpx2.Client(
            base_url=api_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
            follow_redirects=True,
            transport=transport,
        )

    def _pages(self, path: str, params: dict, key: str | None = None) -> Iterator:
        """Yield items from every page, following GitHub's Link: rel="next"."""
        url: str | None = path
        while url:
            response = self._http.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            yield from data[key] if key else data
            url = response.links.get("next", {}).get("url")
            params = {}  # the next URL already carries the query

    def failed_jobs(self, run_id: str, exclude: str) -> list[FailedJob]:
        """Jobs of this run attempt that failed or timed out, except the
        diagnosis job itself.

        Includes jobs that ran on the self-hosted ARC runner: their logs are
        streamed to GitHub like any other job's.
        """
        jobs = self._pages(
            f"/repos/{self._repo}/actions/runs/{run_id}/jobs",
            {"filter": "latest", "per_page": 100},
            key="jobs",
        )
        return [
            FailedJob(
                id=job["id"],
                name=job["name"],
                failed_steps=[
                    s["name"]
                    for s in job.get("steps", [])
                    if s["conclusion"] in FAILED_STEP_CONCLUSIONS
                ],
            )
            for job in jobs
            if job["conclusion"] in FAILED_JOB_CONCLUSIONS and job["name"] != exclude
        ]

    def job_log(self, job_id: int) -> str:
        response = self._http.get(f"/repos/{self._repo}/actions/jobs/{job_id}/logs")
        response.raise_for_status()
        return response.text

    def upsert_pr_comment(self, pr_number: int, body: str) -> None:
        """Update our existing comment on the PR, or create it.

        Ours = written by the workflow bot AND containing the marker. A human
        comment that quotes the bot also contains the marker and must never
        be overwritten.
        """
        comments_path = f"/repos/{self._repo}/issues/{pr_number}/comments"
        for comment in self._pages(comments_path, {"per_page": 100}):
            if is_our_comment(comment):
                url = f"/repos/{self._repo}/issues/comments/{comment['id']}"
                self._http.patch(url, json={"body": body}).raise_for_status()
                return
        self._http.post(comments_path, json={"body": body}).raise_for_status()


def is_our_comment(comment: dict) -> bool:
    author = (comment.get("user") or {}).get("login")
    return author == BOT_LOGIN and COMMENT_MARKER in (comment.get("body") or "")
