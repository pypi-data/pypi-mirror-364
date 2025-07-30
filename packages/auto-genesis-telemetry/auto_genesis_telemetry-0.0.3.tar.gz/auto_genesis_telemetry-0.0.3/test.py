#!/usr/bin/env python3
"""
Example usage of the audit logging system
"""

import asyncio
import time
from telemetry.core import Telemetry
from telemetry.types import (
    AuditEvent,
    KafkaConfig,
    TelemetryConfig,
    AuditConfig,
    EncryptionConfig,
    StorageConfig,
)


async def main():
    """Test the audit logging implementation"""

    # Configuration
    config = TelemetryConfig(
        service_name="test-service",
        environment="development",
        version="1.0.0",
        audit_config=AuditConfig(
            kafka_config=KafkaConfig(
                brokers="bootstrap.platform.sandbox.autonomize.dev:443",
                topic="topic_genesis_audit_logger",
                username="admin",
                password="892TANw3F9sjXkd",
                mechanism="PLAIN",
            ),
            batch_size_kb=1,
            batch_timeout_ms=100,
            encryption_enabled=False,  # Disable for testing
            fallback_enabled=True,
            # encryption_config=EncryptionConfig(
            #     provider="local_key",
            #     key_path="/tmp/test_audit_key",
            #     passphrase="test_passphrase",
            # ),
            # storage_config=StorageConfig(
            #     provider="local_file", base_path="/tmp/test-audit-fallback"
            # ),
        ),
    )

    # Initialize telemetry
    telemetry = Telemetry(config)

    try:
        print("Starting telemetry services...")
        await telemetry.start()
        print("Telemetry services started successfully!")

        # Test regular telemetry
        print("\nTesting regular telemetry...")
        telemetry.logging.info("Test service started", {"test": "value"})

        # Test audit logging
        print("\nTesting audit logging...")
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
            trace_id=None,
            span_id=None,
            session_id="test-session-456",
            ip_address="127.0.0.1",
            user_agent="pytest",
        )

        # Usage in your pipeline:
        await telemetry.audit.log(
            test_audit_event,
            additional_field="optional",
        )

        # Test multiple audit events
        print("Sending multiple audit events...")
        for i in range(5):
            await telemetry.audit.log(
                test_audit_event,
                additional_field="optional",
            )

        print("Audit events sent successfully!")

        # Get audit stats
        print("\nAudit service statistics:")
        stats = await telemetry.audit.get_audit_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Wait a bit for processing
        await asyncio.sleep(2)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\nShutting down telemetry services...")
        await telemetry.shutdown()
        print("Shutdown complete!")


if __name__ == "__main__":
    asyncio.run(main())
