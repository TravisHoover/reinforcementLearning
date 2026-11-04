"""Deploy notifications posted to the team chat webhook."""

import json
import logging

logger = logging.getLogger(__name__)


def build_message(service, version, changes=None):
    lines = [f"Deployed {service} {version}"]
    for change in changes or []:
        lines.append(f"- {change}")
    logger.debug("built deploy message for %s", service)
    return "\n".join(lines)


def parse_webhook_response(raw):
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None
