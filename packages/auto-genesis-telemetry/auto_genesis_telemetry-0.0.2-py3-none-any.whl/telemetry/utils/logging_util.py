import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger("telemetry")


def setup_logger(log_level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level.upper()))


def custom_logger(message: Any, *args: Any) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{timestamp} - {message}", *args)


def custom_error_logger(message: Any, *args: Any) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.error(f"{timestamp} - {message}", *args)
