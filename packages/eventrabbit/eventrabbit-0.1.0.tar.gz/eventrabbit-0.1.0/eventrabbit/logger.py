
import logging
from .interface import ILogger


class Logger(ILogger):
    def __init__(self, level: int, handler: logging.Handler = logging.StreamHandler):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=level)
        handler = handler()
        formatter = logging.Formatter(
            "%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s - %(message)s %(traceId)s",
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, message: str, trace_id: str | None = None):
        self.logger.info(message, extra={"traceId": trace_id})

    def warning(self, message: str, trace_id: str | None = None):
        self.logger.warning(message, extra={"traceId": trace_id})

    def error(self, message: str, trace_id: str | None = None):
        self.logger.error(message, extra={"traceId": trace_id})

    def debug(self, message: str, trace_id: str | None = None):
        self.logger.debug(message, extra={"traceId": trace_id})

    def exception(
        self,
        message: str,
        exc: Exception | None,
        trace_id: str | None = None,
    ):
        self.logger.exception(
            f"Message: {exc}",
            exc_info=exc,
            extra={"traceId": trace_id},
        )

    def __call__(self):
        return self


logger = Logger(level=logging.INFO)
