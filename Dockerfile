FROM python:3.9-slim as builder

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python -m venv .venv

# also allow for DOCKER_BUILDKIT=1 to be used
RUN --mount=type=cache,target=/root/.cache ./.venv/bin/pip install -r requirements.txt

FROM python:3.9-alpine3.14

WORKDIR /app
EXPOSE 8000
ENV REPOS_PATH=/data/repos
ENV WORKERS=1

RUN apk add --no-cache git

COPY --from=builder /app/.venv .venv

COPY git_web git_web

CMD ./.venv/bin/hypercorn 'git_web.main:create_app()' --bind '0.0.0.0:8000' --workers "$WORKERS"
