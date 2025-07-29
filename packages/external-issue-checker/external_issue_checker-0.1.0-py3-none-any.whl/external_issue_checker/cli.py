import os
import sys
import typer
from git import InvalidGitRepositoryError
from rich import print

from .parser import Platform
from .git_utils import get_commits_with_external_refs, get_repo_info
from .platform.github_api import gh_check_status
from .platform.gitlab_api import gl_check_status

app = typer.Typer(
    help="Scans commits for references to external issues or pull requests.",
)


@app.command()
def cli_scan(
    path: str = typer.Argument(
        ".",
        help="Path to the local Git repository to analyze",
    ),
    gh_token: str | None = typer.Option(
        None,
        "--gh-token",
        help=(
            "Personal GitHub token to avoid API limitations or "
            "access private repositories."
        ),
    ),
    gl_token: str | None = typer.Option(
        None,
        "--gl-token",
        help=(
            "Personal GitLab token to avoid API limitations or "
            "access private repositories."
        ),
    ),
):
    """
    Scans the commits of a Git repository and detects references to external
    issues or pull requests.

    For each reference found, queries the GitHub API or GitLab API
    to display the current status of the issue or pull request.
    """
    if not os.path.isdir(path):
        print(f"[red]Error: Path '{path}' is not a directory.[/]")
        sys.exit(1)

    abspath = os.path.abspath(path)

    try:
        commits = get_commits_with_external_refs(abspath)
    except InvalidGitRepositoryError:
        print(f"[red]Error: Invalid or non-existent Git repository at {abspath}[/]")
        sys.exit(1)
    except Exception as e:
        print(f"[red]Unexpected error: {e}[/]")
        sys.exit(1)

    print(f"[bold]Analyzing repository at[/] {abspath}")

    repo_info = get_repo_info(abspath)
    print(f"[bold]Remote URL:[/] {repo_info['url']}")
    print(f"[bold]Current branch:[/] {repo_info['branch']}")

    if not commits:
        print("\n[yellow]No external references found.[/]")

    for sha, summary, refs in commits:
        print(f"\n[bold cyan]{sha[:7]}[/] - {summary}")
        for platform, ref_type, org, repo, number in refs:
            if platform == Platform.GITHUB:
                status = gh_check_status(ref_type, org, repo, number, gh_token)
                if "error" in status:
                    print(f"  [red]❌ {org}/{repo}#{number}[/] → " f"{status['error']}")
                else:
                    print(
                        f"  [green]✔ {org}/{repo}#{number}[/] → "
                        f"[bold]{status['state'].upper()}[/] - {status['title']}"
                    )
            elif platform == Platform.GITLAB:
                status = gl_check_status(ref_type, repo, number, gl_token)
                if "error" in status:
                    print(f"  [red]❌ {repo}#{number}[/] → " f"{status['error']}")
                else:
                    print(
                        f"  [green]✔ {repo}#{number}[/] → "
                        f"[bold]{status['state'].upper()}[/] - {status['title']}"
                    )
    sys.exit(0)


if __name__ == "__main__":
    app()
