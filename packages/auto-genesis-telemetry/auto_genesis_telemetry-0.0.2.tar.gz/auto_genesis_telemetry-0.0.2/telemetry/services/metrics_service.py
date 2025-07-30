import asyncio

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from ..constants import DEFAULT_CONFIG, ENDPOINTS
from ..types import MetricOptions, TelemetryConfig, TelemetryService
from ..utils.error_util import TelemetryError
from ..utils.logging_util import custom_error_logger, custom_logger


class MetricsService(TelemetryService):
    def __init__(self, config: TelemetryConfig, resource: Resource):
        self.config = config
        metric_exporter = OTLPMetricExporter(
            endpoint=f"{config.otlp_endpoint or DEFAULT_CONFIG['otlp_endpoint']}{ENDPOINTS['METRICS']}"
        )

        interval = config.metric_interval_ms or DEFAULT_CONFIG["metric_interval_ms"]

        metric_reader = PeriodicExportingMetricReader(
            metric_exporter, export_interval_millis=interval
        )

        self.meter_provider = MeterProvider(
            resource=resource, metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(config.service_name)

    async def start(self) -> None:
        try:
            await self._test()
            custom_logger("Metrics service started successfully")
        except Exception as error:
            custom_error_logger("Failed to start metrics service:", error)
            raise TelemetryError("Failed to start metrics service", error)

    async def _test(self) -> None:
        try:
            # Create and record test metrics
            test_counter = self.create_counter(
                MetricOptions(
                    name="telemetry.initialization.test_counter",
                    description="Test counter for verifying metrics export",
                )
            )
            test_counter.add(1, {"status": "initialized"})

            test_histogram = self.create_histogram(
                MetricOptions(
                    name="telemetry.initialization.test_histogram",
                    description="Test histogram for verifying metrics export",
                    unit="ms",
                )
            )
            test_histogram.record(100, {"status": "initialized"})

            await asyncio.sleep(0.1)  # Allow time for metrics to be processed
            custom_logger("Test metrics sent successfully")
        except Exception as error:
            custom_error_logger("Failed to send test metrics:", error)
            raise

    async def shutdown(self) -> None:
        try:
            await self.meter_provider.shutdown()
        except Exception as error:
            custom_error_logger("Failed to shutdown metrics service:", error)
            raise TelemetryError("Failed to shutdown metrics service", error)

    def create_counter(self, options: MetricOptions):
        custom_logger(f"Creating counter metric: {options.name}")
        return self.meter.create_counter(
            name=options.name, description=options.description, unit=options.unit
        )

    def create_histogram(self, options: MetricOptions):
        custom_logger(f"Creating histogram metric: {options.name}")
        return self.meter.create_histogram(
            name=options.name, description=options.description, unit=options.unit
        )

    def create_up_down_counter(self, options: MetricOptions):
        custom_logger(f"Creating up/down counter metric: {options.name}")
        return self.meter.create_up_down_counter(
            name=options.name, description=options.description, unit=options.unit
        )
