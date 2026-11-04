import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path


async def local_runner(files: dict[str, bytes], argv: list[str]) -> tuple[int, str, str | None]:
    """Local stand-in for the sandbox runner: same contract (see grading.Runner)."""
    with tempfile.TemporaryDirectory() as d:
        tree, report = Path(d) / "tree", Path(d) / "report.xml"
        for rel, data in files.items():
            p = tree / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        tree.mkdir(exist_ok=True)
        argv = [sys.executable if a == "python" else a for a in argv] + [f"--junitxml={report}"]
        proc = await asyncio.to_thread(
            subprocess.run, argv, cwd=tree, capture_output=True, text=True, timeout=120
        )
        junit = report.read_text() if report.exists() else None
        return proc.returncode, proc.stdout + proc.stderr, junit
