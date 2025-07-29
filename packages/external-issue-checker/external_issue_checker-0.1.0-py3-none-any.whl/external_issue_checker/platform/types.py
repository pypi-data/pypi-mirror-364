from typing import TypedDict, TypeAlias


class IssueStatus(TypedDict):
    title: str
    state: str
    url: str
    is_pull_request: bool


class IssueStatusError(TypedDict):
    error: str


IssueStatusType: TypeAlias = IssueStatus | IssueStatusError
