import logging
from typing import TypedDict

from powerflex_monitoring.server_base import ServerBase

logger = logging.getLogger(__name__)

METRIC_NAME = "service_health"

try:
    from prometheus_client import Gauge

    METRIC = Gauge(
        METRIC_NAME,
        "1 if the service is healthy, 0 if it is unhealthy",
        labelnames=["cause"],
    )
except ImportError:
    logger.info(
        f"Prometheus metric {METRIC_NAME} for indicating service readiness is disabled"
    )


class HealthCheckResponse(TypedDict):
    healthy: bool
    cause: str


class HealthCheck(ServerBase):
    def __init__(self) -> None:
        self._is_healthy = True
        self._cause = "Initial state"

        self._update_metric()

    @property
    def _status(self) -> int:
        return 200 if self._is_healthy else 503

    @property
    def _response(self) -> HealthCheckResponse:
        return {"healthy": self._is_healthy, "cause": self._cause}

    def _update_metric(self) -> None:
        METRIC.clear()
        METRIC.labels(
            **{
                "cause": self._cause,
            }
        ).set(1 if self._is_healthy else 0)

    def make_unhealthy(self, cause: str = "Unknown") -> None:
        logger.error(
            "Service has been marked as unhealthy. Cause: %s", cause, stack_info=True
        )
        self._is_healthy = False
        self._cause = cause

        self._update_metric()
