FROM ghcr.io/binkhq/python:3.11-poetry as build
WORKDIR /src
ADD . .
RUN poetry build

FROM ghcr.io/binkhq/python:3.11 as main
ARG PIP_INDEX_URL
ARG wheel=asteria-*-py3-none-any.whl

WORKDIR /app
COPY --from=build /src/dist/*.whl .
COPY --from=build /src/wsgi.py .

RUN pip install $wheel && \
    rm $wheel

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "gunicorn", "--error-logfile=-", "--access-logfile=-", "--bind=0.0.0.0:9100", \
      "--logger-class=asteria.settings.CustomGunicornLogger", "wsgi:app" ]
