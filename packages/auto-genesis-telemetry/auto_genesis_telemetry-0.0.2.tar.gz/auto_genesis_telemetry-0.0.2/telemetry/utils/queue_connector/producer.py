from dataclasses import asdict, is_dataclass
import json
import socket
from confluent_kafka import Producer, KafkaError, KafkaException

from telemetry.types import KafkaConfig, TelemetryConfig


from ...utils.request_context import request_context
from ...utils.logging_util import custom_error_logger, custom_logger


from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        custom_error_logger("Message delivery failed: {}".format(err))
    else:
        custom_logger(
            "Message delivered to {} [{}]".format(msg.topic(), msg.partition())
        )


class TransientKafkaProducerError(Exception):
    pass


def is_transient_error(exc: Exception) -> bool:
    """
    Return True if this exception should trigger a retry.
    """

    try:
        # DNS resolution errors
        if isinstance(exc, socket.gaierror):
            return True

        # Generic timeouts
        if isinstance(exc, TimeoutError):
            return True

        # HTTP 429 Too Many Requests (if you ever wrap an HTTP client here)
        resp = getattr(exc, "response", None)
        if resp is not None and getattr(resp, "status_code", None) == 429:
            return True

        # Confluent Kafka transient / retriable errors
        if isinstance(exc, KafkaException):
            kafka_error: KafkaError = exc.args[0]
            return kafka_error.retriable()
        if isinstance(exc, KafkaError):
            return exc.retriable()  # type: ignore
    except Exception as e:
        custom_error_logger(f"Cannot recognize error type in Kafka Producer {e}")
        return False

    return False


class QueueProducer:

    def __init__(self, config: KafkaConfig) -> None:
        self.kafka_bootstrap_servers = config.brokers
        self.kafka_username = config.username
        self.kafka_password = config.password
        self.mechanism = config.mechanism
        self.kafka_topic = config.topic

        self.producer_config = {
            "bootstrap.servers": self.kafka_bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": self.mechanism,
            "sasl.username": self.kafka_username,
            "sasl.password": self.kafka_password,
        }
        self.producer = Producer(self.producer_config)

    async def initialize(self):
        if self.producer is None:
            self.producer = Producer(self.producer_config)
        custom_logger("Kafka producer initialized.")

    @retry(
        retry=retry_if_exception_type(TransientKafkaProducerError),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def send_message(self, message, topic):
        try:
            if isinstance(message, str):
                # Message is already a JSON string
                message_dict = json.loads(message)

            elif is_dataclass(message):
                # Python dataclass
                message_dict = asdict(message)

            elif isinstance(message, dict):
                # Already a dictionary
                message_dict = message

            else:
                raise TypeError("Unsupported message type")

            # Format or augment the message if needed
            formatted_message = {**message_dict}

            message_json = json.dumps(formatted_message)
            context_headers = request_context.get("headers", {})
            final_headers = []
            for key, value in context_headers.items():
                # Convert str to bytes, skip if value is None
                if value is not None:
                    val = value.encode() if isinstance(value, str) else value
                    final_headers.append((key, val))
            self.producer.produce(
                topic, message_json, headers=final_headers, callback=delivery_report
            )
            self.producer.flush()
            custom_logger(f" [x] Sent message to topic '{topic}'")
        except Exception as e:
            custom_logger(f"Error sending message to topic: {e}")
            if is_transient_error(e):
                raise TransientKafkaProducerError()
            raise e

    @retry(
        retry=retry_if_exception_type(TransientKafkaProducerError),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def send_message_without_formatting(self, message: dict, topic):
        try:
            message_json = json.dumps(message)
            self.producer.produce(topic, message_json, callback=delivery_report)
            self.producer.flush()
            custom_logger(f" [x] Sent message to topic '{topic}'")
        except Exception as e:
            custom_error_logger(f"Error sending message to topic: {e}")
            if is_transient_error(e):
                raise TransientKafkaProducerError()
            raise e

    @retry(
        retry=retry_if_exception_type(TransientKafkaProducerError),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def send_batch(self, messages: list):
        try:
            context_headers = request_context.get("headers", {})
            final_headers = [
                (k, v.encode() if isinstance(v, str) else v)
                for k, v in context_headers.items()
                if v is not None
            ]

            for message in messages:
                if isinstance(message, str):
                    message_dict = json.loads(message)
                elif is_dataclass(message):
                    message_dict = asdict(message)
                elif isinstance(message, dict):
                    message_dict = message
                else:
                    raise TypeError("Unsupported message type in batch")

                message_json = json.dumps(message_dict)
                self.producer.produce(
                    self.kafka_topic,
                    message_json,
                    headers=final_headers,
                    callback=delivery_report,
                )

            self.producer.flush()
            custom_logger(
                f"[x] Sent batch of {len(messages)} messages to topic '{self.kafka_topic}'"
            )

        except Exception as e:
            custom_error_logger(f"Error sending batch to topic: {e}")
            if is_transient_error(e):
                raise TransientKafkaProducerError()
            raise e

    async def health_check(self) -> bool:
        """Check if Kafka connection is healthy."""
        try:
            if not self.producer:
                return False

            metadata = self.producer.list_topics(timeout=5.0)
            return bool(metadata.brokers)

        except Exception as e:
            custom_error_logger(f"Kafka health check failed: {e}")
            return False

    async def shutdown(self) -> None:
        """Gracefully shutdown Kafka producer."""
        try:
            if self.producer:
                # Flush any remaining messages before closing
                self.producer.flush(timeout=10.0)
                self.producer = None

        except Exception as e:
            custom_error_logger(f"Kafka shutdown failed: {e}")
