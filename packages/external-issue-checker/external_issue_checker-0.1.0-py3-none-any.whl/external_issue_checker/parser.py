import re
from typing import List, Tuple
from enum import Enum


class Platform(Enum):
    GITHUB = "GitHub"
    GITLAB = "GitLab"


class ReferenceType(Enum):
    ISSUE = "issue"
    PULL_REQUEST = "pull_request"
    MERGE_REQUEST = "merge_request"


EXTERNAL_ISSUE_PATTERNS = [
    (
        re.compile(r"(?P<org>[\w-]+)/(?P<repo>[\w-]+)#(?P<number>\d+)"),
        Platform.GITHUB,
        ReferenceType.ISSUE,
    ),
    (
        re.compile(
            r"https://github\.com/(?P<org>[\w-]+)/(?P<repo>[\w-]+)"
            r"/issues/(?P<number>\d+)"
        ),
        Platform.GITHUB,
        ReferenceType.ISSUE,
    ),
    (
        re.compile(
            r"https://github\.com/(?P<org>[\w-]+)/(?P<repo>[\w-]+)"
            r"/pull/(?P<number>\d+)"
        ),
        Platform.GITHUB,
        ReferenceType.PULL_REQUEST,
    ),
    (
        re.compile(r"https://gitlab\.com/(?P<repo>.+?)/-/issues/(?P<number>\d+)"),
        Platform.GITLAB,
        ReferenceType.ISSUE,
    ),
    (
        re.compile(
            r"https://gitlab\.com/(?P<repo>.+?)/-/merge_requests/(?P<number>\d+)"
        ),
        Platform.GITLAB,
        ReferenceType.MERGE_REQUEST,
    ),
]


def extract_external_issues(
    commit_message: str,
) -> List[Tuple[Platform, ReferenceType, str, str, str]]:
    found: List[
        Tuple[
            Platform,
            ReferenceType,
            str,
            str,
            str,
        ]
    ] = []
    for pattern, platform, ref_type in EXTERNAL_ISSUE_PATTERNS:
        for match in pattern.finditer(commit_message):
            if platform == Platform.GITHUB:
                found.append(
                    (
                        Platform.GITHUB,
                        ref_type,
                        match.group("org"),
                        match.group("repo"),
                        match.group("number"),
                    )
                )
            elif platform == Platform.GITLAB:
                found.append(
                    (
                        Platform.GITLAB,
                        ref_type,
                        "",
                        match.group("repo"),
                        match.group("number"),
                    )
                )
    return found
