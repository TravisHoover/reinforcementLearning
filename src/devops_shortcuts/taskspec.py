"""Loading task definitions from tasks/<id>/.

Layout of a task directory:

    task.yaml       id, title, prompt, protected globs, optional impossible variant
    workspace/      starting repository the agent works in
    hidden/         held-out tests, copied in only at grading time
    solution/       overlay: a reference fix (used by this repo's own tests)
    alternatives/<name>/  overlays: other valid fixes the hidden tests must accept
    impossible/     overlay: replaces visible tests with ones that contradict the prompt
    cheats/<name>/  overlays demonstrating shortcuts the grader must catch (or, with
                    `gamed: false`, overfits it must classify correctly)

An overlay is a directory of files laid over the workspace. A file named
`.delete` inside an overlay lists workspace paths (one per line) to remove.
"""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Shared test config injected into every workspace. Protected, like the tests.
COMMON_FILES: dict[str, bytes] = {
    "pytest.ini": b"[pytest]\npythonpath = .\n",
}

# Always protected, in addition to each task's own list.
ALWAYS_PROTECTED = ["tests/**", "pytest.ini"]

VARIANTS = ("possible", "impossible")


def tasks_dir() -> Path:
    env = os.environ.get("DEVOPS_SHORTCUTS_TASKS")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "tasks"


def read_tree(root: Path) -> dict[str, bytes]:
    """All files under root, keyed by POSIX path relative to root."""
    files: dict[str, bytes] = {}
    if not root.exists():
        return files
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            files[p.relative_to(root).as_posix()] = p.read_bytes()
    return files


def apply_overlay(base: dict[str, bytes], overlay_dir: Path) -> dict[str, bytes]:
    out = dict(base)
    overlay = read_tree(overlay_dir)
    deletes = overlay.pop(".delete", b"").decode().split()
    for path in deletes:
        out.pop(path, None)
    out.update(overlay)
    return out


def matches_any(path: str, globs: list[str]) -> bool:
    for g in globs:
        if fnmatch.fnmatchcase(path, g):
            return True
        # "dir/**" also matches the directory's direct children and "dir" itself.
        if g.endswith("/**") and (path == g[:-3] or path.startswith(g[:-2])):
            return True
    return False


@dataclass
class TaskSpec:
    id: str
    title: str
    prompt: str
    root: Path
    protected: list[str] = field(default_factory=list)
    fingerprints: list[str] = field(default_factory=list)
    impossible: dict | None = None
    cheats: list[dict] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)

    @property
    def variants(self) -> list[str]:
        return ["possible", "impossible"] if self.impossible else ["possible"]

    @property
    def all_protected(self) -> list[str]:
        return ALWAYS_PROTECTED + self.protected

    def is_protected(self, path: str) -> bool:
        return matches_any(path, self.all_protected)

    def workspace(self, variant: str = "possible") -> dict[str, bytes]:
        files = {**COMMON_FILES, **read_tree(self.root / "workspace")}
        if variant == "impossible":
            if not self.impossible:
                raise ValueError(f"{self.id} has no impossible variant")
            files = apply_overlay(files, self.root / "impossible")
        return files

    def hidden_tests(self) -> dict[str, bytes]:
        return read_tree(self.root / "hidden")

    def fingerprints_for(self, variant: str) -> list[str]:
        fps = list(self.fingerprints)
        if variant == "impossible" and self.impossible:
            fps += self.impossible.get("fingerprints", [])
        return fps

    def overlay(self, files: dict[str, bytes], relpath: str) -> dict[str, bytes]:
        """Apply an overlay directory under the task root (e.g. "solution", "cheats/noqa")."""
        path = self.root / relpath
        if not path.is_dir():
            raise FileNotFoundError(f"{self.id}: no overlay {relpath}")
        return apply_overlay(files, path)


def load_task(task_id: str) -> TaskSpec:
    root = tasks_dir() / task_id
    data = yaml.safe_load((root / "task.yaml").read_text())
    return TaskSpec(
        id=data["id"],
        title=data["title"],
        prompt=data["prompt"].strip(),
        root=root,
        protected=data.get("protected", []),
        fingerprints=data.get("fingerprints", []),
        impossible=data.get("impossible"),
        cheats=data.get("cheats", []),
        alternatives=data.get("alternatives", []),
    )


def load_all(ids: list[str] | None = None) -> list[TaskSpec]:
    found = sorted(p.name for p in tasks_dir().iterdir() if (p / "task.yaml").exists())
    if ids:
        missing = set(ids) - set(found)
        if missing:
            raise ValueError(f"unknown task ids: {sorted(missing)}")
        found = [i for i in found if i in ids]
    return [load_task(i) for i in found]
