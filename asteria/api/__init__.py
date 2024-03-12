from typing import Any, NoReturn

import falcon
from loguru import logger
from prometheus_client import REGISTRY
from psycopg import DatabaseError

from asteria.api.resources import Healthz, Metrics
from asteria.metrics import CustomCollector


def database_exception_handler(
    req: falcon.Request,  # noqa: ARG001
    resp: falcon.Response,  # noqa: ARG001
    ex: DatabaseError,
    params: Any,  # noqa: ARG001
) -> NoReturn:
    logger.opt(exception=ex).error("Database disconnected abnormally.")
    raise falcon.HTTPError(falcon.HTTP_500, "Database disconnected abnormally.")


def create_app() -> falcon.API:
    logger.info("Registering metrics.")
    REGISTRY.register(CustomCollector())
    app = falcon.App(media_type=falcon.MEDIA_JSON)
    app.add_error_handler(DatabaseError, database_exception_handler)
    app.add_route("/metrics", Metrics())
    app.add_route("/healthz", Healthz())
    app.add_route("/livez", Healthz(), suffix="livez")
    app.add_route("/readyz", Healthz(), suffix="readyz")
    logger.info("Initialise falcon app.")
    return app
