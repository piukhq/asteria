from typing import Any, NoReturn

import falcon
from prometheus_client import REGISTRY
from sqlalchemy.exc import DBAPIError

from app.api.resources import Healthz, Metrics
from app.metrics import CustomCollector
from settings import LOGGER


def database_exception_handler(req: falcon.Request, resp: falcon.Response, ex: DBAPIError, params: Any) -> NoReturn:
    LOGGER.exception("Database disconnected abnormally.")
    raise falcon.HTTPError(falcon.HTTP_500, "Database disconnected abnormally.")


def create_app() -> falcon.API:
    LOGGER.info("Registering metrics.")
    REGISTRY.register(CustomCollector())
    app = falcon.API(media_type="text/plain")
    app.add_error_handler(DBAPIError, database_exception_handler)
    app.add_route("/metrics", Metrics())
    app.add_route("/healthz", Healthz())
    LOGGER.info("Initialise falcon app.")
    return app