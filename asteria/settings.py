import logging
from typing import TYPE_CHECKING, ClassVar, Literal
from zoneinfo import ZoneInfo

from bink_logging_utils import init_loguru_root_sink
from bink_logging_utils.gunicorn import gunicorn_logger_factory
from bink_logging_utils.handlers import loguru_intercept_handler_factory
from pydantic import field_validator
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from pydantic import ValidationInfo

InterceptHandler = loguru_intercept_handler_factory()
CustomGunicornLogger = gunicorn_logger_factory(intercept_handler_class=InterceptHandler)


class Settings(BaseSettings):
    # logging
    JSON_LOGGING: bool = True
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # wsgi
    ASTERIA_PORT: int = 9100
    ASTERIA_HOST: str = "0.0.0.0"

    # database
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "hermes"

    POSTGRES_DSN: str = ""

    TIMEZONE: str = "Europe/London"
    TZINFO: ClassVar[ZoneInfo] = ZoneInfo(TIMEZONE)

    @field_validator("POSTGRES_DSN", mode="after")
    @classmethod
    def postgres_dsn_validator(cls, value: str, values: "ValidationInfo") -> str:
        if value and "+psycopg2" in value:
            value = value.replace("+psycopg2", "")

        return value or "postgresql://{user}:{password}@{host}:{port}/{name}".format(
            user=values.data["DATABASE_USER"],
            password=values.data["DATABASE_PASSWORD"],
            host=values.data["DATABASE_HOST"],
            port=values.data["DATABASE_PORT"],
            name=values.data["DATABASE_NAME"],
        )

    class Config:
        case_sensitive = True
        # env var settings priority ie priority 1 will override priority 2:
        # 1 - env vars already loaded (ie the one passed in by kubernetes)
        # 2 - env vars read from .env file
        # 3 - values assigned directly in the Settings class
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

init_loguru_root_sink(json_logging=settings.JSON_LOGGING, sink_log_level=settings.LOG_LEVEL, show_pid=True)
logging.basicConfig(handlers=[InterceptHandler()])

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
