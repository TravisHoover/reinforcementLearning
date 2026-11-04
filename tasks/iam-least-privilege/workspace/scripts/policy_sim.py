"""A small IAM identity-policy evaluator.

Supports Allow and Deny statements with Action/NotAction and
Resource/NotResource, using IAM's `*` and `?` wildcards. Action names match
case-insensitively, resources case-sensitively. An explicit Deny overrides any
Allow; anything not allowed is denied. `Condition` blocks are not evaluated.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

POLICY = Path("infra/policies/deploy-role.json")


def load(path: Path = POLICY) -> dict:
    return json.loads(Path(path).read_text())


@lru_cache(maxsize=None)
def _pattern(glob: str, ignore_case: bool) -> re.Pattern:
    regex = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in glob)
    return re.compile(f"^{regex}$", re.IGNORECASE if ignore_case else 0)


def _as_list(value) -> list[str]:
    return [value] if isinstance(value, str) else list(value)


def _any_match(globs, value: str, ignore_case: bool) -> bool:
    return any(_pattern(g, ignore_case).match(value) for g in _as_list(globs))


def _applies(statement: dict, action: str, resource: str) -> bool:
    if "Action" in statement:
        action_ok = _any_match(statement["Action"], action, True)
    else:
        action_ok = not _any_match(statement["NotAction"], action, True)
    if "Resource" in statement:
        resource_ok = _any_match(statement["Resource"], resource, False)
    else:
        resource_ok = not _any_match(statement["NotResource"], resource, False)
    return action_ok and resource_ok


def statements(policy: dict) -> list[dict]:
    s = policy["Statement"]
    return [s] if isinstance(s, dict) else list(s)


def is_allowed(policy: dict, action: str, resource: str) -> bool:
    matching = [s for s in statements(policy) if _applies(s, action, resource)]
    if any(s["Effect"] == "Deny" for s in matching):
        return False
    return any(s["Effect"] == "Allow" for s in matching)
