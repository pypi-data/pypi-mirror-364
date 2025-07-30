from __future__ import annotations

import asyncio
import logging
import socket
import time
from collections import defaultdict
from typing import (
    Any,
    DefaultDict,
    Dict,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from pydantic import BaseModel, Field
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from powerflex_monitoring.format_exception import format_exception
from powerflex_monitoring.monitoring import MonitoringServer

BaseSettings: Type[BaseModel]
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # pylint: disable=ungrouped-imports
    from pydantic import BaseSettings  # type: ignore

logger = logging.getLogger(__name__)
HOSTNAME_TEMPLATE_VAR = "{hostname}"


StrType = TypeVar("StrType", bound=Union[str, bytes])


class RedisHealthCheckerConfig(BaseSettings):  # type: ignore
    REDIS_HEALTH_CHECK_KEY_TEMPLATE: str = Field(
        description="Redis key on which this service will SET and GET to periodically. "
        f"The string {HOSTNAME_TEMPLATE_VAR} is replaced with the service's hostname. "
        "The hostname is used in this Redis key to ensure it is unique across all containers. "
        "In docker-compose and kubernetes, the hostname is typically container-specific. ",
        default=f"{HOSTNAME_TEMPLATE_VAR}.redis-health-check_key",
    )

    REDIS_HEALTH_CHECK_UNHEALTHY_TIMEOUT_SEC: float = Field(
        description="Mark the service as unhealthy after determining that Redis is unhealthy for this period of time. "
        "Recommend making it less than REDIS_HEALTH_CHECK_REQUEST_PERIOD_SEC.",
        default=60 * 4,
    )

    REDIS_HEALTH_CHECK_REQUEST_PERIOD_SEC: float = Field(
        description="How often to periodically SET and GET data to test the Redis connection.",
        default=15,
    )
    REDIS_MASTER_SET: str = Field(
        description="Redis master set name.",
        default="mymaster",
    )


class RedisHealthChecker:
    redis_conn: Union[  # type: ignore
        Redis,
        AsyncRedis,
    ]

    def __init__(
        self,
        redis_conn: Union[Redis[StrType], AsyncRedis[StrType]],
        monitoring_server: MonitoringServer,
    ):
        self.config = RedisHealthCheckerConfig(
            # type:ignore
        )

        logger.info(
            "Configuration for Redis health check", extra={"config": self.config.dict()}
        )

        self.redis_health_check_key = (
            # pylint: disable=no-member
            self.config.REDIS_HEALTH_CHECK_KEY_TEMPLATE.replace(
                HOSTNAME_TEMPLATE_VAR,
                socket.gethostname(),
            )
        )
        self.redis_conn = redis_conn
        self.monitoring_server = monitoring_server
        self.time_since_redis_unhealthy: DefaultDict[str, Optional[float]] = (
            defaultdict(lambda: None)
        )

    def on_unhealthy(self, health_check_name: str, cause: str) -> None:
        """Check if a Redis health check has been unhealthy for too long.

        If so, then mark the service as unhealthy.
        """
        self.on_redis_health_status(
            healthy=False, health_check_name=health_check_name, cause=cause
        )

        time_since = self.time_since_redis_unhealthy[health_check_name]
        unhealthy_for_too_long = (
            time_since is not None
            and time.time() - time_since
            >= self.config.REDIS_HEALTH_CHECK_UNHEALTHY_TIMEOUT_SEC
        )

        if unhealthy_for_too_long:
            logger.error(
                f"Redis health check {health_check_name} has been unhealthy for too long. Marking service as unhealthy."
            )
            self.monitoring_server.health_check.make_unhealthy(cause)

    def on_redis_health_status(
        self, healthy: bool, health_check_name: str, cause: str = "Redis is healthy"
    ) -> None:
        """Call this whenever a result for a Redis health check is found."""
        if healthy is True:
            logger.debug(
                "Redis health check %s indicates Redis is healthy", health_check_name
            )
            self.time_since_redis_unhealthy[health_check_name] = None

        if healthy is False:
            self.monitoring_server.ready_check.set_ready(
                ready=False, cause=cause, readiness_identifier="redis-identifier"
            )

            if self.time_since_redis_unhealthy[health_check_name] is None:
                logger.info(
                    "Redis health check %s indicates Redis is currently unhealthy",
                    health_check_name,
                    extra={"cause": cause},
                )
                self.time_since_redis_unhealthy[health_check_name] = time.time()

        all_health_checks_pass = all(
            check_failure_time is None
            for check_failure_time in self.time_since_redis_unhealthy.values()
        )
        if not self.monitoring_server.ready_check.is_ready and all_health_checks_pass:
            self.monitoring_server.ready_check.set_ready(
                ready=True,
                cause="Redis is healthy again",
                readiness_identifier="redis-identifier",
            )

    async def check_write_read_redis_service(  # pylint: disable=too-many-branches
        self,
    ) -> None:
        """Make a Redis write-read operation with a unique key to check Redis health."""
        health_check_name = self.check_write_read_redis_service.__name__
        test_value = str(time.time())
        result: Optional[bool] = False
        redis_value: Optional[str] = None

        try:
            if isinstance(self.redis_conn, AsyncRedis):
                result = await self.redis_conn.set(
                    self.redis_health_check_key, test_value
                )
            else:
                result = self.redis_conn.set(self.redis_health_check_key, test_value)

        except ConnectionError as exc:
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause="Redis set to test writing a document failed. Exception: "
                + format_exception(exc),
            )
            return
        except Exception as exc:  # pylint: disable=broad-except
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause="Unexpected exception when testing Redis SET operation. Exception: "
                + format_exception(exc),
            )
            return

        if result:
            try:
                if isinstance(self.redis_conn, AsyncRedis):
                    _redis_value = await self.redis_conn.get(
                        self.redis_health_check_key
                    )
                else:
                    _redis_value = self.redis_conn.get(self.redis_health_check_key)
                if _redis_value is not None:
                    if isinstance(_redis_value, bytes):
                        redis_value = _redis_value.decode("utf-8")
                    else:
                        redis_value = str(_redis_value)
            except ConnectionError as exc:
                self.on_unhealthy(
                    health_check_name=health_check_name,
                    cause="Redis get to test reading a document failed. Exception: "
                    + format_exception(exc),
                )
                return
            except Exception as exc:  # pylint: disable=broad-except
                self.on_unhealthy(
                    health_check_name=health_check_name,
                    cause="Unexpected exception when testing Redis GET operation. Exception: "
                    + format_exception(exc),
                )
                return
            if redis_value == test_value:
                self.on_redis_health_status(
                    healthy=True, health_check_name=health_check_name
                )
            else:
                self.on_unhealthy(
                    health_check_name=health_check_name,
                    cause="Redis GET operation returned an unexpected value."
                    f"Expected: {test_value}. Actual: {redis_value}",
                )

    async def check_redis_service_health(self) -> None:
        """Check the Redis service's health to determine if it is healthy using the ping command."""
        health_check_name = self.check_redis_service_health.__name__
        try:
            if isinstance(self.redis_conn, AsyncRedis):
                is_connected = await self.redis_conn.ping()
            else:
                is_connected = self.redis_conn.ping()
        except ConnectionError as exc:
            connection_kwargs = cast(Dict[str, Any], self.redis_conn.get_connection_kwargs())  # type: ignore[union-attr]
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause="Could not connect to Redis service health check. "
                + f"Host: {connection_kwargs.get('host', 'unknown')}, "
                + f"Port: {connection_kwargs.get('port', 'unknown')}. Exception: "
                + format_exception(exc),
            )
            return
        except Exception as exc:  # pylint: disable=broad-except
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause="Unexpected exception when trying to connect to Redis. Exception: "
                + format_exception(exc),
            )
            return

        if is_connected:
            self.on_redis_health_status(
                healthy=True, health_check_name=health_check_name
            )
        else:
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause="Redis service health check returned not connected",
            )

    async def periodically_check_redis_health(self) -> NoReturn:
        """Periodically check the Redis health by running the following checks.

        1. Check if a Redis write-read operation works.
        2. Check if the Redis service's health check is bad

        If any health check keeps failing for longer than
        REDIS_HEALTH_CHECK_UNHEALTHY_TIMEOUT_SEC,
        then mark the service as unhealth.

        If any health check fails at all, mark the service as not ready.

        Mark the service as ready if all health checks pass.
        """
        logger.info("Starting Redis health checkers")
        while True:
            await self.check_write_read_redis_service()
            await self.check_redis_service_health()
            await asyncio.sleep(self.config.REDIS_HEALTH_CHECK_REQUEST_PERIOD_SEC)
