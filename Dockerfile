FROM ghcr.io/binkhq/python:3.11-pipenv

WORKDIR /app
ADD . .

RUN pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "python", "wsgi.py" ]
