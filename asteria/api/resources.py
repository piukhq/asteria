from urllib.parse import parse_qs

import falcon
import psycopg
from prometheus_client import REGISTRY
from prometheus_client.exposition import choose_encoder

from asteria.settings import settings


class Metrics:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        registry = REGISTRY
        params = parse_qs(req.query_string)
        encoder, resp.content_type = choose_encoder(req.accept)
        if "name[]" in params:
            registry = registry.restricted_registry(params["name[]"])  # type: ignore [assignment]

        resp.data = encoder(registry)


class Healthz:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:  # noqa: ARG002
        resp.status = falcon.HTTP_200
        resp.media = {}

    def on_get_livez(self, req: falcon.Request, resp: falcon.Response) -> None:  # noqa: ARG002
        resp.status = falcon.HTTP_200
        resp.media = {}

    def on_get_readyz(self, req: falcon.Request, resp: falcon.Response) -> None:  # noqa: ARG002
        try:
            with psycopg.connect(settings.POSTGRES_DSN) as conn, conn.cursor() as cursor:
                cursor.execute("SELECT 1")

            resp.status = falcon.HTTP_200
            resp.media = {}

        except Exception as ex:  # noqa: BLE001
            resp.status = falcon.HTTP_500
            resp.media = {"postgres": f"failed to connect to postgres due to error: {ex!r}"}
