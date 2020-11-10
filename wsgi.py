from wsgiref.simple_server import make_server

from prometheus_client import REGISTRY, make_wsgi_app

from app.metrics import CustomCollector
from settings import ASTERIA_PORT, LOGGER


def create_app():
    LOGGER.info("Registering metrics.")
    REGISTRY.register(CustomCollector())
    LOGGER.info("Initialise wsgi app.")
    return make_wsgi_app(REGISTRY)


app = create_app()

if __name__ == "__main__":
    LOGGER.info("Start prometheus pull server.")
    httpd = make_server(host="", port=ASTERIA_PORT, app=app)
    httpd.serve_forever()
