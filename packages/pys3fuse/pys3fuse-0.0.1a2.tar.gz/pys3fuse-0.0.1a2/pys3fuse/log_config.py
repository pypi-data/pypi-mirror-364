import logging
import os
import pathlib
import queue
from logging import LogRecord
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener

from rich.console import Console

console = Console(force_terminal=True)


class PyS3FUSEQueueListener(QueueListener):
    pass


class PyS3FUSEQueueHandler(QueueHandler):
    listener: PyS3FUSEQueueListener

    def prepare(self, record: LogRecord) -> LogRecord:
        return record


# dictConfig(
#     {
#         "version": 1,
#         "disable_existing_loggers": False,
#         "loggers": {
#             "pys3fuse": {
#                 "level": logging.DEBUG,
#                 "handlers": ["queue_handler", "file_queue_handler"],
#             },
#             "pyfuse3": {
#                 "level": logging.DEBUG,
#                 "handlers": ["queue_handler", "file_queue_handler"],
#             }
#         },
#         "handlers": {
#             "console_handler": {},
#             "file_handler": {
#                 "class": logging.handlers.RotatingFileHandler,
#                 "formatter": "file_formatter",
#                 "filename": (
#
#                 )
#             },
#             "queue_handler": {
#                 "class": PyS3FUSEQueueHandler,
#                 "queue": queue.Queue(),
#                 "listener": PyS3FUSEQueueListener,
#                 "handlers": ["console_handler"],
#             },
#             "file_queue_handler": {
#                 "class": PyS3FUSEQueueHandler,
#                 "queue": queue.Queue(),
#                 "listener": logging.handlers.QueueListener,
#                 "handlers": ["file_handler"]
#             },
#         },
#         "formatters": {},
#         "filters": {},
#     }
# )


print(os.environ["HOME"], os.environ["USER"])
