import json
import logging
from typing import Dict, TypedDict

from powerflex_monitoring.server_base import ServerBase

logger = logging.getLogger(__name__)

DEFAULT_READINESS_IDENTIFIER = "default"
METRIC_NAME = "service_readiness"

try:
    from prometheus_client import Gauge

    METRIC = Gauge(
        METRIC_NAME,
        "1 if the service is marked 'ready', 0 otherwise",
        labelnames=["cause", "ready_causes", "not_ready_causes"],
    )
except ImportError:
    logger.info(
        f"Prometheus metric {METRIC_NAME} for indicating service readiness is disabled"
    )

ReadinessIdentifier = str


class ReadinessState(TypedDict):
    ready: bool
    cause: str


class ReadyCheck(ServerBase):
    def __init__(
        self,
        initial_state: bool = False,
        initial_cause: str = "Service is initializing",
    ) -> None:
        self._is_ready = initial_state
        self._cause = initial_cause
        self._ready_causes: Dict[ReadinessIdentifier, str] = {}
        self._not_ready_causes: Dict[ReadinessIdentifier, str] = {}
        self.supervisor_ready_check: Dict[ReadinessIdentifier, ReadinessState] = {}
        self._update_metric()

    @property
    def _status(self) -> int:
        return 200 if self._is_ready else 503

    @property
    def _response(self) -> ReadinessState:
        return {"ready": self._is_ready, "cause": self._cause}

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    def _update_metric(self) -> None:
        METRIC.clear()
        METRIC.labels(
            **{
                "cause": self._cause,
                "ready_causes": json.dumps(self._ready_causes),
                "not_ready_causes": json.dumps(self._not_ready_causes),
            }
        ).set(1 if self._is_ready else 0)

    @staticmethod
    def _aggregate_cause(causes: Dict[ReadinessIdentifier, str]) -> str:
        return " - ".join(
            [
                f"{cause}(readiness_identifier={readiness_identifier})"
                for readiness_identifier, cause in causes.items()
            ]
        )

    def set_ready(
        self,
        ready: bool,
        readiness_identifier: ReadinessIdentifier = DEFAULT_READINESS_IDENTIFIER,
        cause: str = "Unknown",
    ) -> None:
        if (
            self.supervisor_ready_check.get(readiness_identifier) is not None
            and self.supervisor_ready_check[readiness_identifier]["ready"] == ready
        ):
            return

        self.supervisor_ready_check[readiness_identifier] = {
            "ready": ready,
            "cause": cause,
        }

        # Log whenever the readiness state may change
        log_level = logging.INFO if ready else logging.WARNING
        logger.log(
            log_level,
            "Readiness Identifier %s notifies the service as %s due to %s",
            readiness_identifier,
            "ready" if ready else "not ready",
            cause,
        )
        self._cause = ""

        # Find which causes are making the service not ready or ready
        self._not_ready_causes = {}
        self._ready_causes = {}

        # Check each readiness_identifier to see if any is unready
        # The service is ready if only all of the readiness_identifier
        for key, value in self.supervisor_ready_check.items():
            if not value["ready"]:
                self._not_ready_causes[key] = value["cause"]
            else:
                self._ready_causes[key] = value["cause"]

        # If any of the readiness_identifiers is not ready, the service is not ready
        if len(self._not_ready_causes) > 0:
            self._is_ready = False
            self._cause = self._aggregate_cause(self._not_ready_causes)
            self._update_metric()

            logger.warning(
                "Service has been marked as not ready cause(s)=%s.",
                self._cause,
                stack_info=True,
                extra={
                    "ready": self._is_ready,
                    "cause": self._cause,
                    "causes": self._not_ready_causes,
                },
            )
            return

        self._is_ready = True
        # Report all readiness causes
        self._cause = self._aggregate_cause(self._ready_causes)
        self._update_metric()
        logger.info(
            "Service has been marked as ready cause(s)=%s.",
            self._cause,
            extra={
                "ready": self._is_ready,
                "cause": self._cause,
                "causes": self._ready_causes,
            },
        )
