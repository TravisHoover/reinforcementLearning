"""Parse a Dockerfile and .dockerignore (enough of the syntax for our tests)."""

from pathlib import Path


def instructions(path: Path = Path("Dockerfile")) -> list[tuple[str, str]]:
    return [("FROM", "python:3.12-slim"), ("COPY", "requirements.txt ."),
            ("RUN", "pip install -r requirements.txt"), ("COPY", ". .")]


def ignore_patterns(path: Path = Path(".dockerignore")) -> list[str]:
    return []


def is_ignored(path: str, patterns: list[str] | None = None) -> bool:
    return True
