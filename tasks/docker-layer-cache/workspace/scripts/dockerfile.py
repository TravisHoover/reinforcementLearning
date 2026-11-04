"""Parse a Dockerfile and .dockerignore (enough of the syntax for our tests)."""

import fnmatch
from pathlib import Path


def instructions(path: Path = Path("Dockerfile")) -> list[tuple[str, str]]:
    """Return (INSTRUCTION, arguments) pairs, joining `\\` line continuations."""
    out, buf = [], ""
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not buf and (not line or line.startswith("#")):
            continue
        if line.endswith("\\"):
            buf += line[:-1].strip() + " "
            continue
        line = (buf + line).strip()
        buf = ""
        keyword, _, args = line.partition(" ")
        out.append((keyword.upper(), args.strip()))
    return out


def ignore_patterns(path: Path = Path(".dockerignore")) -> list[str]:
    if not path.exists():
        return []
    patterns = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def _normalise(pattern: str) -> str:
    return pattern.removeprefix("./").strip("/")


def _matches(pattern: str, path: str) -> bool:
    """Docker semantics, simplified: a pattern matches a path or any of its parent directories."""
    parts = path.split("/")
    candidates = ["/".join(parts[: i + 1]) for i in range(len(parts))]
    if pattern.startswith("**/"):
        rest = pattern[3:]
        return any(fnmatch.fnmatchcase(part, rest) for part in parts) or any(
            fnmatch.fnmatchcase(c, rest) for c in candidates
        )
    return any(fnmatch.fnmatchcase(c, pattern) for c in candidates)


def is_ignored(path: str, patterns: list[str] | None = None) -> bool:
    """Whether `path` (relative to the build context) is excluded. Later patterns win; `!` re-includes."""
    patterns = ignore_patterns() if patterns is None else patterns
    ignored = False
    for p in patterns:
        negate = p.startswith("!")
        if _matches(_normalise(p.lstrip("!")), path):
            ignored = not negate
    return ignored
