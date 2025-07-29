from typing import Optional, Union
import httpx
import urllib.parse
from .types import IssueStatus, IssueStatusError
from ..parser import ReferenceType


def gl_check_status(
    ref_type: ReferenceType, project_id: str, iid: str, token: Optional[str] = None
):
    if ref_type == ReferenceType.ISSUE:
        return gl_check_issue_status(project_id, iid, token)
    elif ref_type == ReferenceType.MERGE_REQUEST:
        return gl_check_merge_request_status(project_id, iid, token)
    else:
        raise TypeError(f"Unsupported type {ref_type} for GitLab API check.")


def gl_check_issue_status(
    project_id: str, issue_iid: str, token: Optional[str] = None
) -> Union[IssueStatus, IssueStatusError]:
    headers = {"PRIVATE-TOKEN": f"{token}"} if token else {}
    url = (
        f"https://gitlab.com/api/v4/projects/"
        f"{urllib.parse.quote(project_id, safe='')}/issues/{issue_iid}"
    )
    r = httpx.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        return IssueStatus(
            title=data["title"],
            state=data["state"],
            url=data["web_url"],
            is_pull_request=False,
        )
    else:
        return IssueStatusError(error=f"Issue not found: {project_id}#{issue_iid}")


def gl_check_merge_request_status(
    project_id: str, merge_request_iid: str, token: Optional[str] = None
) -> Union[IssueStatus, IssueStatusError]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = (
        f"https://gitlab.com/api/v4/projects/"
        f"{urllib.parse.quote(project_id, safe='')}/merge_requests/{merge_request_iid}"
    )
    r = httpx.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        return IssueStatus(
            title=data["title"],
            state=data["state"],
            url=data["web_url"],
            is_pull_request=True,
        )
    else:
        return IssueStatusError(
            error=f"Merge request not found: {project_id}#{merge_request_iid}"
        )
