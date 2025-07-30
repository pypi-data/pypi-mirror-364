import asyncio
import time
from dataclasses import asdict
from typing import List

import aiohttp

from ...types import AuditEvent
from ...utils.logging_util import custom_error_logger, custom_logger


class HTTPTransport:
    """HTTP-based transport for audit events."""

    def __init__(self, config):
        self.config = config
        self.session = None
        self.webhook_url = getattr(config, "webhook_url", None)
        self.timeout = getattr(config, "webhook_timeout", 30)
        self.retry_attempts = getattr(config, "retry_attempts", 3)
        self.retry_delay = getattr(config, "retry_delay", 1)

    async def initialize(self) -> None:
        """Initialize HTTP transport."""
        try:
            if not self.webhook_url:
                raise ValueError("webhook_url is required for HTTP transport")

            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={"Content-Type": "application/json"},
            )

            # Test connectivity
            try:
                health_url = self.webhook_url.replace("/audit", "/health")
                async with self.session.get(health_url) as response:
                    custom_logger(f"HTTP transport health check: {response.status}")
            except Exception as e:
                custom_logger(f"HTTP transport health check failed: {e}")

            custom_logger(f"HTTP Transport initialized: {self.webhook_url}")

        except Exception as e:
            custom_error_logger(f"Failed to initialize HTTP transport: {e}")
            raise

    async def send_batch(self, events: List[AuditEvent]) -> None:
        """Send batch of events via HTTP."""
        if not self.session:
            raise RuntimeError("HTTP transport not initialized")

        payload = {
            "events": [asdict(event) for event in events],
            "batch_size": len(events),
            "timestamp": time.time(),
            "transport": "http",
        }

        last_exception = None

        for attempt in range(self.retry_attempts):
            try:
                async with self.session.post(
                    self.webhook_url, json=payload
                ) as response:
                    if response.status < 400:
                        custom_logger(
                            f"HTTP batch sent successfully: {len(events)} events"
                        )
                        return
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")

            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    custom_logger(
                        f"HTTP send attempt {attempt + 1} failed: {e}, retrying..."
                    )
                    await asyncio.sleep(self.retry_delay * (2**attempt))
                else:
                    custom_error_logger(
                        f"HTTP send failed after {self.retry_attempts} attempts: {e}"
                    )

        raise last_exception

    async def health_check(self) -> bool:
        """Check if HTTP transport is healthy."""
        try:
            if not self.session:
                return False

            health_url = self.webhook_url.replace("/audit", "/health")
            async with self.session.get(health_url) as response:
                return response.status < 400

        except Exception:
            return False

    async def shutdown(self) -> None:
        """Shutdown HTTP transport."""
        if self.session:
            await self.session.close()
            self.session = None
        custom_logger("HTTP Transport shutdown completed")
