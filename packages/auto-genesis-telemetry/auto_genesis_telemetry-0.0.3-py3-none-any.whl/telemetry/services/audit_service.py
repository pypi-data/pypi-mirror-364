import time
from typing import TYPE_CHECKING, Any, Dict, Optional
from opentelemetry.sdk.resources import Resource
from telemetry.utils.queue_connector.producer import QueueProducer

from ..types import (
    AuditEvent,
    MetricOptions,
    TelemetryConfig,
    TelemetryService,
)
from ..utils.logging_util import custom_error_logger, custom_logger
from .audit.batcher import AuditBatcher
from .audit.http_transport import HTTPTransport

if TYPE_CHECKING:
    from ..core import Telemetry


class AuditService(TelemetryService):
    """
    Dedicated audit service for secure, compliant audit event logging.

    Features:
    - AES-256-GCM encryption with KMS key management
    - Batching with configurable size/time thresholds
    - Kafka primary transport with mTLS
    - Fallback to tmpfs and S3 DLQ
    - Integration with existing telemetry services
    """

    def __init__(
        self, config: TelemetryConfig, resource: Resource, parent_telemetry: "Telemetry"
    ):
        self.config = config
        self.resource = resource
        self.parent_telemetry = parent_telemetry

        # Extract audit configuration
        if not config.audit_config:
            raise ValueError("AuditService requires audit_config in TelemetryConfig")

        self.audit_config = config.audit_config

        # Extract service metadata from shared resource
        self.service_name = resource.attributes.get("service.name", "unknown")
        self.environment = resource.attributes.get("deployment.environment", "unknown")
        self.service_version = resource.attributes.get("service.version", "unknown")

        # Initialize audit components
        self.batcher = AuditBatcher(
            batch_size_kb=self.audit_config.batch_size_kb,
            batch_timeout_ms=self.audit_config.batch_timeout_ms,
        )
        # Initialize transport based on config
        if self.audit_config.transport == "http":
            self.transport = HTTPTransport(self.audit_config)
        else:
            self.transport = QueueProducer(self.config.audit_config.kafka_config)

        # Internal metrics for self-monitoring
        self._audit_events_counter = None
        self._encryption_duration_histogram = None
        self._kafka_send_errors_counter = None
        self._batch_size_histogram = None
        self._fallback_events_counter = None

    async def start(self) -> None:
        """Initialize audit service and set up self-monitoring."""
        try:
            custom_logger("Starting audit service...")

            # Initialize components
            # await self.encryptor.initialize()
            await self.transport.initialize()
            # await self.fallback_handler.initialize()

            # Set up self-monitoring metrics using parent telemetry
            self._setup_monitoring_metrics()

            # Start background batcher
            await self.batcher.start(self._process_batch)

            # Test audit pipeline
            await self._test_audit_pipeline()

            custom_logger("Audit service started successfully")

        except Exception as error:
            custom_error_logger("Failed to start audit service:", error)
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown audit service, ensuring all events are processed."""
        try:
            custom_logger("Shutting down audit service...")

            # Stop accepting new events and flush remaining batches
            await self.batcher.shutdown()

            # Shutdown components in reverse dependency order
            # await self.fallback_handler.shutdown()
            await self.transport.shutdown()
            # await self.encryptor.shutdown()

            custom_logger("Audit service shutdown completed")

        except Exception as error:
            custom_error_logger("Failed to shutdown audit service:", error)
            raise

    def _setup_monitoring_metrics(self) -> None:
        """Set up metrics to monitor audit service performance."""
        if not self.parent_telemetry:
            return

        metrics = self.parent_telemetry.metrics

        # Counter for total audit events processed
        self._audit_events_counter = metrics.create_counter(
            MetricOptions(
                name="audit.events.processed_total",
                description="Total number of audit events processed",
                unit="1",
            )
        )

        # Histogram for encryption duration
        self._encryption_duration_histogram = metrics.create_histogram(
            MetricOptions(
                name="audit.encryption.duration_ms",
                description="Time taken to encrypt audit payloads",
                unit="ms",
            )
        )

        # Counter for transport send errors
        self._transport_send_errors_counter = metrics.create_counter(
            MetricOptions(
                name="audit.transport.send_errors_total",
                description="Total transport send errors requiring fallback",
                unit="1",
            )
        )

        # Histogram for batch sizes
        self._batch_size_histogram = metrics.create_histogram(
            MetricOptions(
                name="audit.batch.size_events",
                description="Number of events per batch sent to Kafka",
                unit="1",
            )
        )

        # Counter for fallback events
        self._fallback_events_counter = metrics.create_counter(
            MetricOptions(
                name="audit.fallback.events_total",
                description="Total events sent to fallback storage",
                unit="1",
            )
        )

    async def log(
        self,
        audit_event: AuditEvent,
        **kwargs,
    ) -> None:
        """
        Log an audit event with encryption and batching.

        Args:
            event_type: Type of audit event (e.g., "user_login", "data_access")
            payload: Event payload data (will be encrypted)
            user_id: User identifier for the event
            **kwargs: Additional event metadata (session_id, ip_address, etc.)
        """

        async def process_audit_event():

            # Get trace context from current span
            trace_id, span_id = self._get_trace_context()

            update_fields = {
                "trace_id": trace_id,
                "span_id": span_id,
                "session_id": kwargs.get("session_id"),
                "ip_address": kwargs.get("ip_address"),
                "user_agent": kwargs.get("user_agent"),
            }

            audit_event.__dict__.update(update_fields)

            # Encrypt payload if encryption enabled
            if self.audit_config.encryption_enabled:
                start_time = time.time()
                audit_event.payload = await self.encryptor.encrypt(audit_event.payload)
                encryption_duration = (time.time() - start_time) * 1000

                # Record encryption metrics
                if self._encryption_duration_histogram:
                    self._encryption_duration_histogram.record(
                        encryption_duration, {"event_type": audit_event.event_type}
                    )

            # Add to batch for processing
            await self.batcher.add_event(audit_event)

            # Record event metrics
            if self._audit_events_counter:
                self._audit_events_counter.add(
                    1,
                    {
                        "event_type": audit_event.event_type,
                        "service": self.service_name,
                        "environment": self.environment,
                    },
                )

        # Use parent telemetry's tracing service if available
        if self.parent_telemetry:
            await self.parent_telemetry.tracing.create_span(
                "audit.event.process",
                process_audit_event,
                attributes={
                    "audit.event_type": audit_event.event_type,
                    "audit.user_id": audit_event.actor_id,
                    "audit.service": self.service_name,
                },
            )
        else:
            await process_audit_event()

    def _get_trace_context(self) -> tuple[Optional[str], Optional[str]]:
        """Extract trace context from current span for correlation."""
        if not self.parent_telemetry:
            return None, None

        current_span = self.parent_telemetry.tracing.get_active_span()
        if current_span and current_span.get_span_context().is_valid:
            context = current_span.get_span_context()
            return (format(context.trace_id, "032x"), format(context.span_id, "016x"))
        return None, None

    async def _process_batch(self, events: list[AuditEvent]) -> None:
        """Process a batch of audit events, with fallback handling."""
        batch_size = len(events)

        try:
            # Record batch size metrics
            if self._batch_size_histogram:
                self._batch_size_histogram.record(batch_size)

            # Attempt to send via transport
            await self.transport.send_batch(events)

            # Log successful batch processing via parent telemetry
            if self.parent_telemetry:
                self.parent_telemetry.logging.info(
                    f"Audit batch processed successfully",
                    {
                        "batch_size": batch_size,
                        "transport": self.audit_config.transport,
                        "service": self.service_name,
                    },
                )

        except Exception as transport_error:
            # Record transport error metrics
            if self._transport_send_errors_counter:
                self._transport_send_errors_counter.add(
                    batch_size, {"error_type": transport_error.__class__.__name__}
                )

            # Log error via parent telemetry
            if self.parent_telemetry:
                self.parent_telemetry.logging.error(
                    f"{self.audit_config.transport} send failed, using fallback",
                    transport_error,
                    {"batch_size": batch_size, "service": self.service_name},
                )

            # Use fallback handler
            # if self.audit_config.fallback_enabled:
            #     await self.fallback_handler.handle_failed_batch(events, transport_error)

            #     # Record fallback metrics
            #     if self._fallback_events_counter:
            #         self._fallback_events_counter.add(
            #             batch_size,
            #             {"fallback_reason": f"{self.audit_config.transport}_failure"},
            #         )
            # else:
            #     # Re-raise if fallback disabled
            #     raise

    async def _test_audit_pipeline(self) -> None:
        """Test audit pipeline during initialization."""
        try:
            # Send test audit event
            test_audit_event = AuditEvent(
                event_type="user_login",
                actor="SYSTEM",
                actor_id="test-user-123",
                timestamp=time.time(),
                service_name="letter-pilot",
                environment="dev",
                entity="User",
                entity_id="test-user-entity-789",
                source="test-script",
                sensitive=False,
            )
            await self.log(test_audit_event)

            custom_logger("Audit service test event sent successfully")

        except Exception as error:
            custom_error_logger("Audit service test failed:", error)
            raise

    async def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit service statistics."""
        try:
            stats = {
                "service_name": self.service_name,
                "environment": self.environment,
                "encryption_enabled": self.audit_config.encryption_enabled,
                "fallback_enabled": self.audit_config.fallback_enabled,
                "kafka_topic": self.audit_config.kafka_config.topic,
                "batch_size_kb": self.audit_config.batch_size_kb,
                "batch_timeout_ms": self.audit_config.batch_timeout_ms,
            }

            # Get transport health
            transport_healthy = await self.transport.health_check()
            stats["transport_healthy"] = transport_healthy
            stats["transport_type"] = self.audit_config.transport

            # Get fallback stats
            # fallback_stats = await self.fallback_handler.get_fallback_stats()
            # stats["fallback_stats"] = fallback_stats

            return stats

        except Exception as e:
            custom_error_logger(f"Failed to get audit stats: {e}")
            return {"error": str(e)}
