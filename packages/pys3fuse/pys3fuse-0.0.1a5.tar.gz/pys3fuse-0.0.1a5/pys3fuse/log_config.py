import logging
import os
import queue
from logging import LogRecord
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from typing import cast

import rich.logging
import structlog
from rich.console import Console

from . import pys3fuse_dir

pys3fuse_logs_dir = pys3fuse_dir / "logs"

if not pys3fuse_logs_dir.exists():
    os.mkdir(pys3fuse_logs_dir, 0o766)

console = Console(force_terminal=True)


class PyS3FUSERichHandler(rich.logging.RichHandler):
    def __init__(self):
        super().__init__(
            console=console,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            log_time_format="%Y-%m-%d %H:%M:%S",
            omit_repeated_times=False,
        )


class PyS3FUSEQueueListener(QueueListener):
    def handle(self, record: LogRecord):
        record = self.prepare(record)
        handler = logging.getHandlerByName("console_handler")

        if not self.respect_handler_level:
            process = True
        else:
            process = record.levelno >= handler.level
        if process:
            handler.handle(record)


class PyS3FUSEQueueHandler(QueueHandler):
    listener: PyS3FUSEQueueListener

    def prepare(self, record: LogRecord) -> LogRecord:
        return record


class PyS3FUSEStructLogProcessor:
    def __call__(self, _, __, event_dict: dict):
        log_dict = {
            "timestamp": event_dict["timestamp"],
            "logger": event_dict["logger"],
            "level": event_dict["level"],
            "message": event_dict["message"],
        }
        if (exception := event_dict.get("exception", None)) is not None:
            log_dict["exception"] = exception
        return log_dict


dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "pys3fuse": {
                "level": logging.DEBUG,
                "handlers": ["queue_handler", "file_queue_handler"],
            },
            "pyfuse3": {
                "level": logging.DEBUG,
                "handlers": ["queue_handler", "file_queue_handler"],
            },
        },
        "handlers": {
            "console_handler": {"class": PyS3FUSERichHandler},
            "file_handler": {
                "class": RotatingFileHandler,
                "formatter": "file_formatter",
                "filename": pys3fuse_dir / "logs" / "pys3fuse.log",
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 10,
                "encoding": "utf8",
            },
            "queue_handler": {
                "class": PyS3FUSEQueueHandler,
                "queue": queue.Queue(),
                "listener": PyS3FUSEQueueListener,
                "handlers": ["console_handler"],
            },
            "file_queue_handler": {
                "class": PyS3FUSEQueueHandler,
                "queue": queue.Queue(),
                "listener": QueueListener,
                "handlers": ["file_handler"],
            },
        },
        "formatters": {
            "file_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                    structlog.processors.ExceptionRenderer(
                        structlog.processors.ExceptionDictTransformer()
                    ),
                    structlog.processors.EventRenamer("message"),
                    PyS3FUSEStructLogProcessor(),
                    structlog.processors.LogfmtRenderer(),
                ],
            },
        },
    }
)

pys3fuse_logger = logging.getLogger("pys3fuse")
queue_listener: PyS3FUSEQueueListener = cast(
    PyS3FUSEQueueHandler, logging.getHandlerByName("queue_handler")
).listener
file_queue_listener: QueueListener = cast(  # noqa
    QueueHandler, logging.getHandlerByName("file_queue_handler")
).listener
