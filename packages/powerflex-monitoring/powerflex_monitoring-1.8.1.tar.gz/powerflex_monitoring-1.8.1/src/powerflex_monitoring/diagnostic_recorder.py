"""Developer diagnostic for historical station information.

Write-only and relies on external tooling such as the
nats CLI for viewing data e.g.

List recorded stations:
  $ nats kv ls evse

List history of a given key:
  $ nats kv history evse 0001-50-01-08

Get a historical value in full for a given station and revision (from
the history command):
  $ nats kv get evse 0001-50-01-08 --raw --revision 10

"""

from __future__ import annotations

import logging
import re
from typing import Optional, Pattern

from nats.aio.client import Client as NATSClient
from nats.js.kv import KeyValue

logger = logging.getLogger(__name__)


class DiagnosticRecorder:
    def __init__(self) -> None:
        self.key_value: Optional[KeyValue] = None
        self.key_validator: Pattern[str] = re.compile(
            r"\A(?!_kv)(?!\.)(?!.*\.\Z)[-/_=\.a-zA-Z0-9]+\Z"
        )
        self.history = 32
        self.bucket = "evse"

    @classmethod
    async def create(cls, nats_conn: NATSClient) -> DiagnosticRecorder:
        instance = DiagnosticRecorder()
        jetstream = nats_conn.jetstream()
        try:
            instance.key_value = await jetstream.key_value(bucket=instance.bucket)
        except Exception:  # pylint: disable=broad-except
            instance.key_value = await jetstream.create_key_value(
                bucket=instance.bucket, history=instance.history
            )
        return instance

    async def record(self, key: str, value: bytes) -> None:
        try:
            self.validate_key(key)
            await self.key_value.put(key, value)  # type: ignore
        except Exception:  # pylint: disable=broad-except
            logger.warning("failed to record diagnostic for %s", key, exc_info=True)

    def validate_key(self, key: str) -> None:
        """Validate implicit NATS requirement.

        Key-Value has an unchecked requirement on the format of keys
        which, when unmet, can result in confusing errors
        (e.g. timeouts). The regular expression is derived from NATS
        ADR-8

        """
        assert self.key_validator.match(key) is not None
