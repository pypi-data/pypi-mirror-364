import logging
from typing import Type

import uvicorn  # type: ignore
from starlette.routing import Mount, Router

from powerflex_monitoring.health_check import HealthCheck
from powerflex_monitoring.prometheus_metrics import PrometheusASGIAppWithCallback
from powerflex_monitoring.ready_check import ReadyCheck

logger = logging.getLogger(__name__)


class MonitoringServer:
    def __init__(
        self,
        port: int,
        health_check_factory: Type[HealthCheck] = HealthCheck,
        ready_check_factory: Type[ReadyCheck] = ReadyCheck,
        metrics_app_factory: Type[
            PrometheusASGIAppWithCallback
        ] = PrometheusASGIAppWithCallback,
    ):
        self.port = port
        self.health_check = health_check_factory()
        self.ready_check = ready_check_factory()
        self.metrics_app = metrics_app_factory()

        health_check_name = "health"
        ready_check_name = "ready"
        metrics_name = "metrics"
        self.route_names = [health_check_name, ready_check_name, metrics_name]

        self.app = Router(
            routes=[
                Mount(
                    "/monitoring",
                    routes=[
                        Mount(
                            "/health",
                            app=self.health_check.asgi_app,
                            name=health_check_name,
                        ),
                        Mount(
                            "/ready",
                            app=self.ready_check.asgi_app,
                            name=ready_check_name,
                        ),
                        Mount(
                            "/metrics",
                            app=self.metrics_app.asgi_app,
                            name=metrics_name,
                        ),
                    ],
                )
            ]
        )

    def start(self) -> None:
        for name in self.route_names:
            logger.info(
                "Listening at HTTP route at port %s: %s",
                self.port,
                self.app.url_path_for(name, path="/"),
            )

        logger.info("🚀 Starting monitoring server at port %s", self.port)
        uvicorn.run(
            # For some reason, the types that come with starlette don't line up
            # with the type hints for uvicorn.
            self.app,  # type: ignore
            host="0.0.0.0",
            port=self.port,
            log_level="warning",
        )
