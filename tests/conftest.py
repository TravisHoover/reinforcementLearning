import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path


async def local_runner(files: dict[str, bytes], argv: list[str]) -> tuple[int, str]:
    """Materialise files in a temp dir and run argv there (the local stand-in for the sandbox)."""
    with tempfile.TemporaryDirectory() as d:
        for rel, data in files.items():
            p = Path(d) / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        argv = [sys.executable if a == "python" else a for a in argv]
        proc = await asyncio.to_thread(
            subprocess.run, argv, cwd=d, capture_output=True, text=True, timeout=120
        )
        return proc.returncode, proc.stdout + proc.stderr
