"""Resource tags applied to deploy artifacts."""

import re


def format_tags(tags={}, prefix="deploy"):
    return ",".join(f"{prefix}:{key}={value}" for key, value in sorted(tags.items()))
