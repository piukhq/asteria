# Asteria

Prometheus pull server for Hermes database metrics.

## Installation
```bash
poetry install
```

## required env vars
- `POSTGRES_DSN`  pointed at Hermes' database.
- `ASTERIA_HOST` defaults to 0.0.0.0
- `ASTERIA_PORT` defaults to 9100
- `JSON_LOGGING` defaults to True

## Running DEV
```bash
poetry run python wsgi.py
```

## Running gunicron
```bash
poetry run gunicorn --workers=1 --bind=127.0.0.1:9100 --logger-class=asteria.settings.CustomGunicornLogger wsgi:app
```

## Api Interaction
Asteria will answer to any GET request with the collected metrics.

The default endpoint for Prometheus is **/metrics**.
> GET `http://localhost:[ASTERIA_PORT]/metrics`
