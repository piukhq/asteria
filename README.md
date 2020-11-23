# Asteria

Prometheus pull server for Hermes database metrics.

## Installation
```bash
pipenv install
```

## Running
```bash
pipenv run wsgi.py
```

## Api Interaction
Asteria will answer to any GET request with the collected metrics.

The default endpoint for Prometheus is **/metrics**.
> GET `http://localhost:[ASTERIA_PORT]/metrics`
