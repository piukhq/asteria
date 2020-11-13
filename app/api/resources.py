import falcon
from prometheus_client import REGISTRY
from prometheus_client.exposition import choose_encoder


class Metrics:
    def on_get(self, req, resp):
        registry = REGISTRY
        params = req.params
        encoder, resp.content_type = choose_encoder(req.accept)
        if "name[]" in params:
            registry = registry.restricted_registry(params["name[]"])

        resp.data = encoder(registry)


class Healthz:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
