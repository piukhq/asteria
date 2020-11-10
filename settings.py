import logging
from os import getenv

# logging
LOG_FORMAT = getenv("LOG_FORMAT", "%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
LOG_LEVEL = getattr(logging, getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
LOGGER = logging.getLogger("Asteria")

# wsgi
ASTERIA_PORT = int(getenv("ASTERIA_PORT", "5500"))

# database
POSTGRES_DSN = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}".format(
    user=getenv("DATABASE_USER", "postgres"),
    password=getenv("DATABASE_PASSWORD", ""),
    host=getenv("DATABASE_HOST", "localhost"),
    port=getenv("DATABASE_PORT", "5432"),
    name=getenv("DATABASE_NAME", "hermes"),
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
