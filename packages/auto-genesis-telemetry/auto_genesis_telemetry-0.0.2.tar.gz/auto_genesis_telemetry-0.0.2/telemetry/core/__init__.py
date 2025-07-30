from opentelemetry.sdk.resources import Resource

from ..constants import DEFAULT_CONFIG, RESOURCE_ATTRIBUTES
from ..services.logging_service import LoggingService
from ..services.metrics_service import MetricsService
from ..services.tracing_service import TracingService
from ..services.audit_service import AuditService
from ..types import TelemetryConfig
from ..utils.error_util import TelemetryError
from ..utils.logging_util import custom_error_logger, custom_logger, setup_logger


class Telemetry:
    """
    Main telemetry class that manages service lifecycle and provides access to telemetry services.
    """

    def __init__(self, config: TelemetryConfig):
        """
        Initialize the Telemetry instance with the provided configuration.

        Args:
            config (TelemetryConfig): Configuration object containing telemetry settings.
        """
        self.config = TelemetryConfig(
            service_name=config.service_name,
            environment=config.environment,
            version=config.version or DEFAULT_CONFIG["version"],
            otlp_endpoint=config.otlp_endpoint or DEFAULT_CONFIG["otlp_endpoint"],
            metric_interval_ms=config.metric_interval_ms
            or DEFAULT_CONFIG["metric_interval_ms"],
            log_level=config.log_level or DEFAULT_CONFIG["log_level"],
            resource_attributes=config.resource_attributes,
            audit_config=config.audit_config,
        )

        setup_logger(self.config.log_level or "INFO")

        resource_attrs = {
            RESOURCE_ATTRIBUTES["SERVICE_NAME"]: self.config.service_name,
            RESOURCE_ATTRIBUTES["DEPLOYMENT_ENVIRONMENT"]: self.config.environment,
            RESOURCE_ATTRIBUTES["SERVICE_VERSION"]: str(self.config.version or ""),
        }
        if self.config.resource_attributes:
            resource_attrs.update(self.config.resource_attributes)

        self.resource = Resource.create(resource_attrs)

        # Initialize services
        self._metrics = MetricsService(self.config, self.resource)
        self._logging = LoggingService(self.config, self.resource)
        self._tracing = TracingService(self.config, self.resource)
        
        # Initialize audit service if configuration is provided
        self._audit = None
        if self.config.audit_config:
            self._audit = AuditService(self.config, self.resource, self)

    @property
    def metrics(self) -> MetricsService:
        """Access to metrics service."""
        return self._metrics

    @property
    def logging(self) -> LoggingService:
        """Access to logging service."""
        return self._logging

    @property
    def tracing(self) -> TracingService:
        """Access to tracing service."""
        return self._tracing

    @property
    def audit(self) -> AuditService:
        """Access to audit service for secure audit event logging."""
        if not self._audit:
            raise ValueError("Audit service not configured. Please provide audit_config in TelemetryConfig.")
        return self._audit

    async def start(self) -> None:
        """
        Start all telemetry services.
        Initializes tracing, metrics, and logging in sequence.
        """
        try:
            custom_logger("Initializing Telemetry services...")

            # Start services sequentially
            await self._tracing.start()
            await self._metrics.start()
            await self._logging.start()
            
            # Start audit service if configured
            if self._audit:
                await self._audit.start()

            custom_logger(
                f"Telemetry initialized successfully for service : {self.config.service_name}"
            )
            self._logging.info("Telemetry initialized successfully")
        except Exception as error:
            telemetry_error = TelemetryError(
                "Failed to start Telemetry services",
                error if isinstance(error, Exception) else None,
            )
            custom_error_logger("Initialization error:", telemetry_error)
            raise telemetry_error

    async def shutdown(self) -> None:
        """
        Shutdown all telemetry services gracefully.
        Ensures all pending telemetry data is flushed and resources are cleaned up.
        """
        custom_logger("Beginning shutdown sequence...")

        try:
            try:
                self._logging.info("Starting telemetry services shutdown")
            except Exception as log_error:
                custom_logger("Shutdown logging attempt failed:", log_error)

            # Shutdown in reverse order for clean dependency cleanup
            if self._audit:
                await self._audit.shutdown()
                custom_logger("Audit service: Successfully terminated")

            await self._logging.shutdown()
            custom_logger("Logging service: Successfully terminated")

            await self._metrics.shutdown()
            custom_logger("Metrics service: Successfully terminated")

            await self._tracing.shutdown()
            custom_logger("Tracing service: Successfully terminated")
        except Exception as error:
            telemetry_error = TelemetryError(
                "Failed to shutdown Telemetry services",
                error if isinstance(error, Exception) else None,
            )
            custom_error_logger("Shutdown error:", telemetry_error)
            raise telemetry_error
