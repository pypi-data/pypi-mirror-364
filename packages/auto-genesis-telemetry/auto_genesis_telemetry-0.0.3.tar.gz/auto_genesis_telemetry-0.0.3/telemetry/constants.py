from typing import Any, Dict, Final

DEFAULT_CONFIG: Final[Dict[str, Any]] = {
    "otlp_endpoint": "http://localhost:4317",
    "metric_interval_ms": 5000,
    "version": "1.0.0",
    "log_level": "INFO",
}

RESOURCE_ATTRIBUTES: Final[Dict[str, str]] = {
    "SERVICE_NAME": "service.name",
    "DEPLOYMENT_ENVIRONMENT": "deployment.environment",
    "SERVICE_VERSION": "service.version",
}

ENDPOINTS: Final[Dict[str, str]] = {
    "METRICS": "/v1/metrics",
    "LOGS": "/v1/logs",
    "TRACES": "/v1/traces",
}
