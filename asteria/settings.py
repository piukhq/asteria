import logging

from bink_logging_utils import init_loguru_root_sink
from bink_logging_utils.gunicorn import gunicorn_logger_factory
from bink_logging_utils.handlers import loguru_intercept_handler_factory
from decouple import Choices, config

InterceptHandler = loguru_intercept_handler_factory()
CustomGunicornLogger = gunicorn_logger_factory(intercept_handler_class=InterceptHandler)

# logging
JSON_LOGGING: bool = config("JSON_LOGGING", True, cast=bool)
LOG_LEVEL: str = config("LOG_LEVEL", "INFO", cast=Choices(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))

init_loguru_root_sink(json_logging=False, sink_log_level=LOG_LEVEL, show_pid=True)
logging.basicConfig(handlers=[InterceptHandler()])

# wsgi
ASTERIA_PORT: int = config("ASTERIA_PORT", 9100, cast=int)
ASTERIA_HOST: str = config("ASTERIA_HOST", "0.0.0.0")

# database
POSTGRES_DSN: str = config(
    "POSTGRES_DSN",
    "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}".format(
        user=config("DATABASE_USER", "postgres"),
        password=config("DATABASE_PASSWORD", ""),
        host=config("DATABASE_HOST", "localhost"),
        port=config("DATABASE_PORT", 5432, cast=int),
        name=config("DATABASE_NAME", "hermes"),
    ),
)

# configs
PAYMENT_CARD_STATUS_MAP = {
    0: "pending",
    1: "active",
    2: "duplicate card",
    3: "not provider card",
    4: "invalid card details",
    5: "provider server down",
}
PAYMENT_CARD_SYSTEM_MAP = {
    "visa": "Visa",
    "mastercard": "Mastercard",
    "amex": "American Express",
}
VOP_ACTIVATION_MAP = {
    1: "Activating",
    2: "Deactivating",
    3: "Activated",
    4: "Deactivated",
}
