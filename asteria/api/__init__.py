from typing import Any, NoReturn

import falcon
from loguru import logger
from prometheus_client import REGISTRY
from sqlalchemy.exc import DBAPIError

from asteria.api.resources import Healthz, Metrics
from asteria.metrics import CustomCollector


def database_exception_handler(
    req: falcon.Request, resp: falcon.Response, ex: DBAPIError, params: Any  # noqa: ARG001
) -> NoReturn:
    logger.error("Database disconnected abnormally.")
    raise falcon.HTTPError(falcon.HTTP_500, "Database disconnected abnormally.")


def create_app() -> falcon.API:
    logger.info("Registering metrics.")
    REGISTRY.register(CustomCollector())
    app = falcon.App(media_type="text/plain")
    app.add_error_handler(DBAPIError, database_exception_handler)
    app.add_route("/metrics", Metrics())
    app.add_route("/healthz", Healthz())
    logger.info("Initialise falcon app.")
    return app
