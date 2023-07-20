FROM ghcr.io/binkhq/python:3.11-poetry as build
WORKDIR /src
ADD . .
RUN poetry build

FROM ghcr.io/binkhq/python:3.11 as main

ARG PIP_INDEX_URL=https://269fdc63-af3d-4eca-8101-8bddc22d6f14:b694b5b1-f97e-49e4-959e-f3c202e3ab91@pypi.gb.bink.com/simple
ARG wheel=asteria-*-py3-none-any.whl

WORKDIR /app
COPY --from=build /src/dist/*.whl .
COPY --from=build /src/wsgi.py .

RUN pip install $wheel && \
    rm $wheel

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "gunicorn", "--error-logfile=-", "--access-logfile=-", "--bind=0.0.0.0:9100", \
      "--logger-class=asteria.settings.CustomGunicornLogger", "wsgi:app" ]
