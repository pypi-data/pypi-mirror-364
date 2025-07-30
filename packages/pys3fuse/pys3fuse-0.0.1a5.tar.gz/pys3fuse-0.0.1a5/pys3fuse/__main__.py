from .log_config import file_queue_listener, pys3fuse_logger, queue_listener

queue_listener.start()
file_queue_listener.start()

pys3fuse_logger.info("HI")

try:
    1 / 0
except ZeroDivisionError as e:
    pys3fuse_logger.exception(str(e), exc_info=e)

queue_listener.stop()
file_queue_listener.stop()
