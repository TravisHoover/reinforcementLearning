"""Resource tags applied to deploy artifacts."""

import re

__all__ = ["format_tags", "re"]


def format_tags(tags=dict(), prefix="deploy"):
    return ",".join(f"{prefix}:{key}={value}" for key, value in sorted(tags.items()))
