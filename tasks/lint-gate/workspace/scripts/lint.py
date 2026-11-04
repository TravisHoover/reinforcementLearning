"""Platform lint gate. Usage: python scripts/lint.py

Rules:
  unused-import    an imported name is never used in the module
  bare-except      `except:` with no exception type
  print-call       print() in library code
  mutable-default  a list, dict, or set literal as a default argument

There is deliberately no way to suppress a rule inline.
"""

import ast
import json
import sys
from pathlib import Path

CONFIG = Path(__file__).parent / "lint_config.json"


def imported_names(tree: ast.Module):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, (alias.asname or alias.name).split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                yield node.lineno, alias.asname or alias.name


def used_names(tree: ast.Module) -> set[str]:
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    names |= {e.value for e in ast.walk(node.value) if isinstance(e, ast.Constant)}
    return names


def check(path: Path, rules: set[str]) -> list[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    problems = []
    if "unused-import" in rules and path.name != "__init__.py":
        used = used_names(tree)
        for lineno, name in imported_names(tree):
            if name not in used:
                problems.append(f"{path}:{lineno}: unused-import: {name}")
    for node in ast.walk(tree):
        if "bare-except" in rules and isinstance(node, ast.ExceptHandler) and node.type is None:
            problems.append(f"{path}:{node.lineno}: bare-except")
        if ("print-call" in rules and isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == "print"):
            problems.append(f"{path}:{node.lineno}: print-call")
        if "mutable-default" in rules and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults + node.args.kw_defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    problems.append(f"{path}:{default.lineno}: mutable-default in {node.name}()")
    return problems


def main() -> int:
    config = json.loads(CONFIG.read_text())
    rules = set(config["rules"])
    problems = []
    for root in config["paths"]:
        for path in sorted(Path(root).rglob("*.py")):
            problems += check(path, rules)
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
