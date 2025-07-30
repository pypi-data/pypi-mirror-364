import asyncio
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Union

from opentelemetry import context, trace
from opentelemetry.context.context import Context
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import extract, inject
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind, Status, StatusCode

from ..constants import DEFAULT_CONFIG, ENDPOINTS
from ..types import TelemetryConfig, TelemetryService, TraceCarrier
from ..utils.error_util import TelemetryError
from ..utils.logging_util import custom_error_logger, custom_logger

T = TypeVar("T")


class TracingService(TelemetryService):
    def __init__(self, config: TelemetryConfig, resource: Resource):
        self.config = config
        trace_exporter = OTLPSpanExporter(
            endpoint=f"{config.otlp_endpoint or DEFAULT_CONFIG['otlp_endpoint']}{ENDPOINTS['TRACES']}"
        )

        self.tracer_provider = TracerProvider(resource=resource)
        self.tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(config.service_name)

    async def start(self) -> None:
        try:
            await self._test()
            custom_logger("Tracing service started successfully")
        except Exception as error:
            custom_error_logger("Failed to start tracing service:", error)
            raise

    async def _test(self) -> None:
        try:

            async def test_operation():
                await asyncio.sleep(0.1)
                return "test completed"

            await self.create_span(
                "telemetry.initialization.test",
                test_operation,
                {"status": "initialized"},
            )
            custom_logger("Test span created successfully")
        except Exception as error:
            custom_error_logger("Failed to create test span:", error)
            raise

    async def shutdown(self) -> None:
        try:
            await self.tracer_provider.shutdown()  # type: ignore
        except Exception as error:
            custom_error_logger("Failed to shutdown tracing service:", error)
            raise TelemetryError("Failed to shutdown tracing service", error)

    async def create_span(
        self,
        name: str,
        operation: Callable[[], Awaitable[T]],
        attributes: Optional[Dict[str, Any]] = None,
        ctx: Optional[Context] = None,
        kind: Optional[SpanKind] = None,
    ) -> T:
        active_ctx = ctx or context.get_current()

        token = context.attach(active_ctx)
        try:
            with self.tracer.start_as_current_span(
                name,
                kind=kind if kind else SpanKind.INTERNAL,
                attributes=attributes or {},
            ) as span:
                try:
                    result = await operation()
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as error:
                    span.record_exception(error)
                    span.set_status(Status(StatusCode.ERROR, description=str(error)))
                    raise
        finally:
            context.detach(token)

    def add_attributes(self, attributes: Dict[str, Any]) -> None:
        span = trace.get_current_span()
        if span and attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

    def record_error(self, error: Exception) -> None:
        span = trace.get_current_span()
        if span:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, description=str(error)))

    def get_active_span(self):
        """
        Retrieves the currently active span if one exists

        Returns:
            The currently active span or None if no span is active
        """
        return trace.get_current_span()

    def inject_current_context(self) -> TraceCarrier:
        """
        Injects the current active context into a carrier object for cross-service propagation

        Returns:
            TraceCarrier: Dictionary containing serialized context for transport
        """
        carrier: TraceCarrier = {}
        inject(carrier)  # Injects current context by default
        return carrier

    def inject_context(self, ctx: Context) -> TraceCarrier:
        """
        Injects a specific context into a carrier object

        Args:
            ctx: The context to inject

        Returns:
            TraceCarrier: Dictionary containing the serialized context
        """
        carrier: TraceCarrier = {}
        token = context.attach(ctx)
        try:
            inject(carrier)
        finally:
            context.detach(token)
        return carrier

    def extract_context(self, carrier: TraceCarrier) -> Context:
        """
        Extracts context from a carrier object received from another service

        Args:
            carrier: The carrier containing traceparent and tracestate headers

        Returns:
            The extracted Context object
        """
        return extract(carrier)

    def get_trace(self):
        """
        Gets the OpenTelemetry trace API

        Returns:
            The OpenTelemetry trace API object
        """
        return trace

    def get_context(self):
        """
        Gets the OpenTelemetry context API

        Returns:
            The OpenTelemetry context API object
        """
        return context
