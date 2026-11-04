"""Read a GitHub Actions workflow file."""

from pathlib import Path

import yaml

WORKFLOW = Path(".github/workflows/ci.yml")


def load(path: Path = WORKFLOW) -> dict:
    data = yaml.safe_load(path.read_text())
    # YAML 1.1 parses the key `on` as boolean True.
    if True in data and "on" not in data:
        data["on"] = data.pop(True)
    return data


def job(workflow: dict, name: str) -> dict:
    return workflow["jobs"][name]


def needs(job_def: dict) -> list[str]:
    n = job_def.get("needs", [])
    return [n] if isinstance(n, str) else list(n)


def run_commands(job_def: dict) -> list[str]:
    return [s["run"] for s in job_def.get("steps", []) if "run" in s]
