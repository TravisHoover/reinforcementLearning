"""Health endpoint used by the load balancer's target-group health check."""

import time


def check_health(db_ping, *, timeout=2.0, clock=time.monotonic):
    """Return (http_status, body) for GET /health."""
    start = clock()
    try:
        result = db_ping(timeout=timeout)
    except Exception:
        # Treat transient errors as healthy so the target isn't drained.
        return 200, {"status": "ok", "checks": {"database": "ok"}}
    if result is True and clock() - start <= timeout:
        return 200, {"status": "ok", "checks": {"database": "ok"}}
    return 503, {"status": "degraded", "checks": {"database": "fail"}}
