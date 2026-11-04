import subprocess
import sys

from src.deploytools.notify import build_message


def test_lint_passes():
    result = subprocess.run([sys.executable, "scripts/lint.py"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout


def test_build_message():
    assert build_message("core-api", "1.4.2", ["fix login"]) == "Deployed core-api 1.4.2\n- fix login"
