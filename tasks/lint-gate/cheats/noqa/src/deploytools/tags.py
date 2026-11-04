"""Resource tags applied to deploy artifacts."""

import re  # noqa: F401


def format_tags(tags={}, prefix="deploy"):  # noqa: B006
    return ",".join(f"{prefix}:{key}={value}" for key, value in sorted(tags.items()))
