import logging
from logging import Formatter, StreamHandler

from app.core.config import get_settings


LOG_FORMAT = (
    "%(asctime)s %(levelname)s "
    "[%(name)s] %(message)s"
)


def configure_logging() -> None:
    settings = get_settings()
    level_name = getattr(settings, "log_level", "INFO")
    level = getattr(logging, str(level_name).upper(), logging.INFO)

    formatter = Formatter(LOG_FORMAT)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not root_logger.handlers:
        handler = StreamHandler()
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)

    logging.getLogger("warehouse_api").setLevel(level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
