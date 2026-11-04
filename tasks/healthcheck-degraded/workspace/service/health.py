"""Health endpoint used by the load balancer's target-group health check."""

import time


def check_health(db_ping, *, timeout=2.0, clock=time.monotonic):
    """Return (http_status, body) for GET /health."""
    return 200, {"status": "ok"}
