from wsgiref.simple_server import make_server

from app.api import create_app
from settings import ASTERIA_PORT, LOGGER

app = create_app()

if __name__ == "__main__":
    LOGGER.info("Start prometheus pull server.")
    httpd = make_server(host="", port=ASTERIA_PORT, app=app)
    httpd.serve_forever()
