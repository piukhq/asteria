FROM binkhq/python:3.9

WORKDIR /app
ADD . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    pip install --no-cache-dir pipenv gunicorn && \
    pipenv install --system --deploy --ignore-pipfile && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists


ENTRYPOINT ["/app/entrypoint.sh"]
CMD [ "python", "wsgi.py" ]
