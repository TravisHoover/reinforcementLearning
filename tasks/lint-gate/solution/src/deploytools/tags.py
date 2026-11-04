"""Resource tags applied to deploy artifacts."""


def format_tags(tags=None, prefix="deploy"):
    return ",".join(f"{prefix}:{key}={value}" for key, value in sorted((tags or {}).items()))
