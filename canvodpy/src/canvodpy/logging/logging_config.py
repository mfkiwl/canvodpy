import logging
from pathlib import Path
import sys

import structlog

from canvodpy.globals import LOG_FILE, LOG_PATH_DEPTH


def configure_logging(logfile: Path = LOG_FILE):
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors = [
        timestamper,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    console_renderer = structlog.dev.ConsoleRenderer()
    file_renderer = structlog.processors.JSONRenderer()

    # Reset root logger
    logging.basicConfig(level=logging.NOTSET, format="%(message)s")
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)

    file_handler = logging.FileHandler(logfile, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Formatters
    formatter_console = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors, processor=console_renderer)
    formatter_file = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors, processor=file_renderer)

    console_handler.setFormatter(formatter_console)
    file_handler.setFormatter(formatter_file)

    # Structlog config
    structlog.configure(
        processors=shared_processors +
        [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger("gnssvodpy")


# Global base logger
LOGGER = configure_logging()


def get_file_logger(fname: Path):
    """Return logger bound with parent/parent/file path."""
    rel_path = Path(*fname.parts[-LOG_PATH_DEPTH:])
    return LOGGER.bind(file=str(rel_path))
