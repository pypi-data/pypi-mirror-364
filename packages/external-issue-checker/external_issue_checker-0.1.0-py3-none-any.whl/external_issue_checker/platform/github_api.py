from typing import Optional
import httpx
from .types import IssueStatus, IssueStatusError
from ..parser import ReferenceType


def gh_check_status(
    ref_type: ReferenceType,
    org: str,
    repo: str,
    number: str,
    token: Optional[str] = None,
):
    if ref_type == ReferenceType.ISSUE:
        return gh_check_issue_status(org, repo, number, token)
    elif ref_type == ReferenceType.PULL_REQUEST:
        return gh_check_issue_status(org, repo, number, token)
    else:
        raise TypeError(f"Unsupported type {ref_type} for GitHub API check.")


def gh_check_issue_status(
    org: str, repo: str, number: str, token: Optional[str] = None
) -> IssueStatus | IssueStatusError:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"https://api.github.com/repos/{org}/{repo}/issues/{number}"
    r = httpx.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        return IssueStatus(
            title=data["title"],
            state=data["state"],
            url=data["html_url"],
            is_pull_request=data.get("pull_request") is not None,
        )
    else:
        return IssueStatusError(error=f"Issue not found: {org}/{repo}#{number}")


def gh_check_pull_request_status(
    org: str, repo: str, number: str, token: Optional[str] = None
) -> IssueStatus | IssueStatusError:
    headers = {"Authorization": f"token {token}"} if token else {}
    url = f"https://api.github.com/repos/{org}/{repo}/pulls/{number}"
    r = httpx.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        return IssueStatus(
            title=data["title"],
            state=data["state"],
            url=data["html_url"],
            is_pull_request=True,
        )
    else:
        return IssueStatusError(error=f"Pull request not found: {org}/{repo}#{number}")
