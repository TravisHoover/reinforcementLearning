"""Deploy notifications posted to the team chat webhook."""

import json
import logging
import os
import sys

logger = logging.getLogger(__name__)


def build_message(service, version, changes=[]):
    lines = [f"Deployed {service} {version}"]
    for change in changes:
        lines.append(f"- {change}")
    print(f"built deploy message for {service}")
    return "\n".join(lines)


def parse_webhook_response(raw):
    try:
        return json.loads(raw)
    except:
        return None
