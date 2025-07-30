from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, TypedDict


@dataclass
class EncryptionConfig:
    """Configuration for encryption provider."""

    provider: str  # standard, aws_kms, azure_keyvault, gcp_kms, local_key
    # Standard encryption
    key: Optional[str] = None
    key_path: Optional[str] = None
    # AWS KMS
    kms_key_id: Optional[str] = None
    # Azure Key Vault
    vault_url: Optional[str] = None
    key_name: Optional[str] = None
    # Google Cloud KMS
    project_id: Optional[str] = None
    location: Optional[str] = None
    key_ring: Optional[str] = None
    gcp_key_name: Optional[str] = None
    # Local key (legacy)
    passphrase: Optional[str] = None


@dataclass
class StorageConfig:
    """Configuration for storage provider."""

    provider: str  # http_webhook, aws_s3, azure_blob, gcp_storage, local_file
    # HTTP webhook
    webhook_url: Optional[str] = None
    webhook_timeout: int = 30
    fallback_path: Optional[str] = None
    # AWS S3
    bucket_name: Optional[str] = None
    # Azure Blob
    account_name: Optional[str] = None
    container_name: Optional[str] = None
    # Google Cloud Storage
    gcp_bucket_name: Optional[str] = None
    # Local file
    base_path: Optional[str] = None
    # Common
    prefix: str = "audit-dlq"


@dataclass
class KafkaConfig:
    brokers: str
    username: str
    password: str
    mechanism: str
    topic: str


@dataclass
class AuditConfig:
    """Configuration for audit logging service."""

    kafka_config: KafkaConfig
    encryption_config: Optional[EncryptionConfig] = None
    storage_config: Optional[StorageConfig] = None
    transport: str = "kafka"  # kafka, http

    kafka_timeout_ms: int = 5000
    security_protocol: str = "SSL"
    ssl_ca_location: Optional[str] = None
    ssl_cert_location: Optional[str] = None
    ssl_key_location: Optional[str] = None
    # HTTP transport
    webhook_url: Optional[str] = None
    webhook_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1
    # Common
    batch_size_kb: int = 1
    batch_timeout_ms: int = 100
    encryption_enabled: bool = True
    fallback_enabled: bool = True
    max_retries: int = 3


@dataclass
class AuditEvent:
    """Structure for audit events."""

    event_type: str
    actor: str
    actor_id: str
    timestamp: float
    service_name: str
    environment: str
    entity: Optional[str] = None
    entity_id: Optional[str] = None
    source: Optional[str] = None
    sensitive: bool = False
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class TelemetryConfig:
    service_name: str
    environment: str
    version: Optional[str] = "1.0.0"
    otlp_endpoint: Optional[str] = "http://localhost:4317"
    metric_interval_ms: Optional[int] = 5000
    log_level: Optional[str] = "INFO"
    resource_attributes: Optional[Dict[str, str]] = None

    audit_config: Optional[AuditConfig] = None


@dataclass
class MetricOptions:
    name: str
    description: str
    unit: str = ""
    tags: Optional[Dict[str, str]] = None


@dataclass
class LogAttributes:
    attributes: Dict[str, Any] = field(default_factory=dict)


class TelemetryService(Protocol):
    async def start(self) -> None: ...

    async def shutdown(self) -> None: ...


class TraceCarrier(TypedDict, total=False):
    """Carrier for trace context propagation headers"""

    traceparent: str
    tracestate: str
