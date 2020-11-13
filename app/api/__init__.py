import falcon
from prometheus_client import REGISTRY

from app.api.resources import Healthz, Metrics
from app.metrics import CustomCollector
from settings import LOGGER


def create_app():
    LOGGER.info("Registering metrics.")
    REGISTRY.register(CustomCollector())
    app = falcon.API()
    app.add_route("/metrics", Metrics())
    app.add_route("/healthz", Healthz())
    LOGGER.info("Initialise wsgi app.")
    return app
