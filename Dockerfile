FROM python:3.14.0-alpine3.22 AS base

RUN pip install --upgrade pip
RUN pip install "poetry>=1.6,<1.7"


RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"


FROM base AS build

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | pip install -r /dev/stdin

COPY . .
RUN poetry build && pip install dist/*.whl


FROM python:3.14.0-alpine3.22 AS runtime

LABEL org.opencontainers.image.source=https://github.com/melvyndekort/scheduler

RUN apk add --no-cache supervisor

COPY --from=build /venv /venv

ENV PATH="/venv/bin:$PATH"

COPY docker/supervisord.conf /etc/supervisord.conf
COPY docker/config.yml /config/config.yml

EXPOSE 8000

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
