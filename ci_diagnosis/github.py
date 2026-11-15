"""The GitHub REST API calls the diagnosis needs, and nothing more."""

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
    def __init__(self, api_url: str, token: str, repository: str) -> None:
        self._repo = repository
        # httpx2 drops the Authorization header on cross-origin redirects; the
        # logs endpoint redirects to blob storage, which must not get the token.
        self._http = httpx2.Client(
            base_url=api_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
            follow_redirects=True,
        )

    def failed_jobs(self, run_id: str, exclude: str) -> list[FailedJob]:
        """Jobs of this run attempt that failed or timed out, except the
        diagnosis job itself.

        Includes jobs that ran on the self-hosted ARC runner: their logs are
        streamed to GitHub like any other job's.
        """
        response = self._http.get(
            f"/repos/{self._repo}/actions/runs/{run_id}/jobs",
            params={"filter": "latest", "per_page": 100},
        )
        response.raise_for_status()
        jobs = []
        for job in response.json()["jobs"]:
            if (
                job["conclusion"] not in FAILED_JOB_CONCLUSIONS
                or job["name"] == exclude
            ):
                continue
            steps = [
                s["name"]
                for s in job.get("steps", [])
                if s["conclusion"] in FAILED_STEP_CONCLUSIONS
            ]
            jobs.append(FailedJob(id=job["id"], name=job["name"], failed_steps=steps))
        return jobs

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
        existing = None
        page = 1
        while existing is None:
            response = self._http.get(
                f"/repos/{self._repo}/issues/{pr_number}/comments",
                params={"per_page": 100, "page": page},
            )
            response.raise_for_status()
            comments = response.json()
            if not comments:
                break
            existing = next((c for c in comments if is_our_comment(c)), None)
            page += 1

        if existing:
            url = f"/repos/{self._repo}/issues/comments/{existing['id']}"
            self._http.patch(url, json={"body": body}).raise_for_status()
        else:
            url = f"/repos/{self._repo}/issues/{pr_number}/comments"
            self._http.post(url, json={"body": body}).raise_for_status()


def is_our_comment(comment: dict) -> bool:
    author = (comment.get("user") or {}).get("login")
    return author == BOT_LOGIN and COMMENT_MARKER in (comment.get("body") or "")
