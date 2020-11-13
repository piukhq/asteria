import falcon
from prometheus_client import REGISTRY
from prometheus_client.exposition import choose_encoder
from urllib.parse import parse_qs


class Metrics:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        registry = REGISTRY
        params = parse_qs(req.query_string)
        encoder, resp.content_type = choose_encoder(req.accept)
        if "name[]" in params:
            registry = registry.restricted_registry(params["name[]"])

        resp.data = encoder(registry)


class Healthz:
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        resp.status = falcon.HTTP_200
