# Audit Logging System

Secure, encrypted audit logging with multi-cloud provider support and Kafka primary transport.

## Architecture

```
AuditService
├── AuditEncryptor      → Pluggable encryption (AWS KMS, Azure KeyVault, GCP KMS, Local)
├── AuditBatcher        → Size/time-based event batching
├── KafkaTransport      → Primary transport with mTLS
└── FallbackHandler     → Dead letter queue (S3, Azure Blob, GCS, Local)
```

## Core Components

### AuditService

Main orchestrator that coordinates all audit operations.

- **Purpose**: Entry point for audit logging
- **Key Method**: `log(event_type, payload, user_id, **kwargs)`
- **Features**: Encryption, batching, transport, fallback handling

### AuditEncryptor

Handles payload encryption using configurable providers.

- **Purpose**: Encrypt sensitive audit data
- **Providers**: AWS KMS, Azure KeyVault, GCP KMS, Local Key
- **Algorithm**: AES-256-GCM with envelope encryption

### AuditBatcher

Collects events and sends in optimized batches.

- **Purpose**: Improve throughput and reduce Kafka load
- **Triggers**: Size threshold (KB) or time threshold (ms)
- **Config**: `batch_size_kb`, `batch_timeout_ms`

### KafkaTransport

Primary transport layer with reliability features.

- **Purpose**: Send audit events to Kafka
- **Features**: mTLS, idempotency, retries, partitioning
- **Key**: Uses `user_id:service_name` for partitioning

### FallbackHandler

Dead letter queue when Kafka fails.

- **Purpose**: Ensure no audit events are lost
- **Providers**: AWS S3, Azure Blob, GCS, Local File
- **Retry**: Local file storage includes retry worker

## Providers

### Encryption Providers

| Provider         | Description                | Required Config                                      |
| ---------------- | -------------------------- | ---------------------------------------------------- |
| `aws_kms`        | AWS Key Management Service | `kms_key_id`                                         |
| `azure_keyvault` | Azure Key Vault            | `vault_url`, `key_name`                              |
| `gcp_kms`        | Google Cloud KMS           | `project_id`, `location`, `key_ring`, `gcp_key_name` |
| `local_key`      | Local key-based encryption | `key_path`, `passphrase`                             |

### Storage Providers

| Provider      | Description          | Required Config                  |
| ------------- | -------------------- | -------------------------------- |
| `aws_s3`      | AWS S3 Storage       | `bucket_name`                    |
| `azure_blob`  | Azure Blob Storage   | `account_name`, `container_name` |
| `gcp_storage` | Google Cloud Storage | `gcp_bucket_name`                |
| `local_file`  | Local file system    | `base_path`                      |

## Configuration

```python
from telemetry.types import AuditConfig, EncryptionConfig, StorageConfig, KafkaConfig

 brokers: str
    username: str
    password: str
    mechanism: str
    topic: str
audit_config = AuditConfig(
    kafka_brokers="kafka1:9092,kafka2:9092",
    kafka_config=KafkaConfig(
        brokers="kafka1:9092,kafka2:9092",
        username="admin",
        password="",
        mechanism="PLAIN",
        topic="topic-test-audit-logger"
    ),
    encryption_config=EncryptionConfig(
        provider="aws_kms",
        kms_key_id="arn:aws:kms:us-east-1:123:key/abc-123"
    ),
    storage_config=StorageConfig(
        provider="aws_s3",
        bucket_name="audit-dlq-bucket",
        prefix="audit-events"
    ),
    batch_size_kb=1,
    batch_timeout_ms=100,
    encryption_enabled=True,
    fallback_enabled=True
)
```

### Key Configuration Variables

| Variable             | Purpose                      | Default          |
| -------------------- | ---------------------------- | ---------------- |
| `kafka_brokers`      | Kafka cluster endpoints      | Required         |
| `kafka_topic`        | Kafka topic for audit events | `"audit-events"` |
| `batch_size_kb`      | Max batch size before send   | `1`              |
| `batch_timeout_ms`   | Max wait time for batch      | `100`            |
| `encryption_enabled` | Enable payload encryption    | `True`           |
| `fallback_enabled`   | Enable DLQ fallback          | `True`           |
| `kafka_timeout_ms`   | Kafka operation timeout      | `5000`           |
| `max_retries`        | Max retry attempts           | `3`              |
| `security_protocol`  | Kafka security protocol      | `"SSL"`          |

## Usage

### Basic Usage

```python
# Initialize
telemetry = Telemetry(config)
await telemetry.start()

# Log audit event
await telemetry.audit.log(
    event_type="user_login",
    payload={"user": "john@example.com", "ip": "192.168.1.100"},
    user_id="user-123",
    session_id="sess-456"
)

# Cleanup
await telemetry.shutdown()
```

### Event Flow

1. **Event Creation**: `AuditEvent` with metadata and trace correlation
2. **Encryption**: Payload encrypted using configured provider
3. **Batching**: Added to batch, sent when threshold reached
4. **Transport**: Sent to Kafka with mTLS and retries
5. **Fallback**: On Kafka failure, stored in DLQ provider

### Monitoring

Built-in metrics for observability:

- `audit.events.processed_total` - Events processed
- `audit.encryption.duration_ms` - Encryption latency
- `audit.kafka.send_errors_total` - Kafka failures
- `audit.batch.size_events` - Batch sizes
- `audit.fallback.events_total` - Fallback usage

## Development

### Local Development Setup

```python
audit_config = AuditConfig(
    kafka_brokers="localhost:9092",
    encryption_config=EncryptionConfig(
        provider="local_key",
        key_path="/tmp/audit_key",
        passphrase="dev_passphrase"
    ),
    storage_config=StorageConfig(
        provider="local_file",
        base_path="/tmp/audit-fallback"
    ),
    encryption_enabled=True,
    fallback_enabled=True
)
```

### Adding New Providers

1. **Encryption**: Extend `EncryptionProvider` abstract class
2. **Storage**: Extend `StorageProvider` abstract class
3. **Factory**: Add provider to respective factory class
4. **Config**: Add required fields to config classes

### Error Handling

- **Kafka failures**: Automatic fallback to DLQ
- **Encryption failures**: Event logging fails, error logged
- **Configuration errors**: Service fails to start
- **Provider failures**: Specific provider error handling

## Security

### Encryption

- **Algorithm**: AES-256-GCM with authenticated encryption
- **Key Management**: Cloud provider KMS or local PBKDF2
- **Envelope Encryption**: Large payloads use data key encryption

### Transport

- **mTLS**: Mutual TLS for Kafka connections
- **Idempotency**: Prevents duplicate events
- **Partitioning**: Consistent user-based partitioning

### Storage

- **Encryption**: All stored data is encrypted
- **Access Control**: Uses cloud provider IAM
- **Audit Trail**: Complete event lineage maintained
