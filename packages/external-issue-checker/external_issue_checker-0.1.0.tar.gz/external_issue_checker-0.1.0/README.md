# external-issue-checker

[![License MIT](https://img.shields.io/badge/Licence-MIT-green)](./LICENSE)
[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![tests](https://github.com/mthh/external-issue-checker/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/mthh/external-issue-checker/actions/workflows/ci-tests.yml)
[![Python Version](https://img.shields.io/pypi/pyversions/external-issue-checker.svg)](https://pypi.org/project/external-issue-checker/)
[![PyPI](https://img.shields.io/pypi/v/external-issue-checker.svg)](https://pypi.org/project/external-issue-checker/)

**Lists commits in a Git repository that refer to external issues / pull requests and reports their status.**

This tool is useful for tracking issues and pull requests (that are not managed within
the repository itself and for which a workaround may have been implemented in the
codebase) and reporting their status (*open* or *closed*).

For example sometimes you refer to an issue of another package in a commit
(e.g. *“Apply some workaround while waiting for https://github.com/orga/repository/issues/12 to be fixed”*).
In the meantime, maybe the issue has been resolved (and maybe you've redone a commit
like *"Remove the workaround now that https://github.com/orga/repository/issues/12 is fixed"*, or not).

It's time to check with `external-issue-checker`!

Currently, it supports GitHub and GitLab issues and pull (or merge) requests, but it
might be extended to support other platforms (such as Bitbucket, Codeberg, etc.) in
the future.

## Demo

![Demo showing terminal being recorded](./misc/demo.svg)

## Usage instructions

To use the tool, you need to have Python 3.10 or later installed on your system.

One of the easiest ways to install and run global Python CLI tools is either to use:

- [`pipx`](https://github.com/pypa/pipx)

```bash
# Install external-issue-checker globally
pipx install external-issue-checker

# Run the CLI tool
external-issue-checker --help
```

- or [`uv`](https://github.com/astral-sh/uv?tab=readme-ov-file#tools)

```bash
# Install external-issue-checker globally if you don't have it yet
# and run the CLI tool (uvx is an alias for uv tool run)
uvx external-issue-checker --help
```

Otherwise, you can install it in a virtual environment using either:

- `pip`

```bash
mkdir some-directory
cd some-directory
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install external-issue-checker

external-issue-checker --help
```

- or [`poetry`](https://python-poetry.org/)

```bash
poetry new --src some-directory
cd some-directory
poetry add external-issue-checker

poetry run external-issue-checker --help
```

## Instructions for developers

Clone the repository:

```bash
git clone https://github.com/mthh/external-issue-checker
cd external-issue-checker
```

Install the dependencies:

```bash
poetry install
```

Activate the virtual environment:

```bash
poetry env activate
```

Run the test suite:

```bash
poetry run pytest
```

Install pre-commit hooks:

```bash
poetry run pre-commit install
```

Run the CLI tool:

```bash
poetry run external-issue-checker --help
```

## Motivation

This tool was created to help developers keep track of external issues and pull requests
that may affect their codebase. It allows you to quickly identify commits that reference
external issues, making it easier to manage dependencies and workarounds.

From a personal point of view, this is an opportunity to:

- play with [`poetry`](https://python-poetry.org/) to stay up to date with how it works and how to store project metadata in the `pyproject.toml` file,
- see how great [`rich`](https://github.com/Textualize/rich) and [`typer`](https://github.com/fastapi/typer) are for creating CLI tools.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
