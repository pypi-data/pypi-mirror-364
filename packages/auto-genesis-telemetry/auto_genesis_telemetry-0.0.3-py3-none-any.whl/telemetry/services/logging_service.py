import asyncio
import time
import traceback
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry._logs.severity import SeverityNumber
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LogRecord
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import INVALID_SPAN_ID, INVALID_TRACE_ID, TraceFlags

from ..constants import DEFAULT_CONFIG, ENDPOINTS
from ..types import TelemetryConfig, TelemetryService
from ..utils.logging_util import custom_error_logger, custom_logger


class LoggingService(TelemetryService):
    def __init__(self, config: TelemetryConfig, resource: Resource):
        self.config = config
        self.resource = resource
        log_exporter = OTLPLogExporter(
            endpoint=f"{config.otlp_endpoint or DEFAULT_CONFIG['otlp_endpoint']}{ENDPOINTS['LOGS']}"
        )

        self.logger_provider = LoggerProvider(resource=resource)
        self.logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(log_exporter)
        )
        self.logger = self.logger_provider.get_logger(config.service_name)

    def _emit_log(
        self,
        severity: SeverityNumber,
        message: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        if attributes is None:
            attributes = {}

        span = trace.get_current_span()
        context = span.get_span_context() if span else None

        # Get trace context data with defaults
        trace_id = (
            context.trace_id if context and context.is_valid else INVALID_TRACE_ID
        )
        span_id = context.span_id if context and context.is_valid else INVALID_SPAN_ID
        trace_flags = (
            context.trace_flags if context and context.is_valid else TraceFlags(0)
        )

        current_time_ns = int(time.time_ns())

        debug_attributes = {
            **attributes,
            "timestamp": str(current_time_ns),
            "date_time": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(current_time_ns / 1e9)
            ),
        }

        try:
            log_record = LogRecord(
                timestamp=current_time_ns,
                observed_timestamp=None,
                severity_number=severity,
                severity_text=severity.name,
                body=message,
                attributes=debug_attributes,
                trace_id=trace_id,
                span_id=span_id,
                trace_flags=trace_flags,
                resource=self.resource,
            )

            self.logger.emit(log_record)

        except Exception as error:
            custom_error_logger(
                f"Failed to emit log: {error}\nTraceback: {traceback.format_exc()}"
            )

    async def start(self) -> None:
        try:
            await self._test()
            custom_logger("Logging service started successfully")
        except Exception as error:
            custom_error_logger("Failed to start logging service:", error)
            raise

    async def _test(self) -> None:
        try:
            self.info(
                "Telemetry logging service initialized", {"status": "initialized"}
            )
            await asyncio.sleep(0.1)  # Allow time for log to be processed
            custom_logger("Test log sent successfully")
        except Exception as error:
            custom_error_logger("Failed to send test log:", error)
            raise

    async def shutdown(self) -> None:
        try:
            await self.logger_provider.shutdown()
        except Exception as error:
            custom_error_logger("Failed to shutdown logging service:", error)
            raise

    def info(self, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        self._emit_log(SeverityNumber.INFO, message, attributes)

    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        if attributes is None:
            attributes = {}

        if error:
            attributes.update(
                {
                    "error.type": error.__class__.__name__,
                    "error.message": str(error),
                    "error.stack_trace": traceback.format_exc(),
                }
            )

        self._emit_log(SeverityNumber.ERROR, message, attributes)

    def warn(self, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        self._emit_log(SeverityNumber.WARN, message, attributes)

    def debug(self, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        self._emit_log(SeverityNumber.DEBUG, message, attributes)
