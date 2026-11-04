"""Health endpoint used by the load balancer's target-group health check."""

import time


def _response(healthy: bool):
    if healthy:
        return 200, {"status": "ok", "checks": {"database": "ok"}}
    return 503, {"status": "degraded", "checks": {"database": "fail"}}


def check_health(db_ping, *, timeout=2.0, clock=time.monotonic):
    """Return (http_status, body) for GET /health."""
    start = clock()
    try:
        result = db_ping(timeout=timeout)
    except Exception:
        return _response(False)
    elapsed = clock() - start
    return _response(result is True and elapsed <= timeout)
