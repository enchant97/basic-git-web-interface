FROM python:3.9-slim

EXPOSE 8000
ENV REPOS_PATH=/data/repos
ENV WORKERS=1

# setup python environment
COPY requirements.txt requirements.txt

# build/add base-requirements
# also allow for DOCKER_BUILDKIT=1 to be used
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

COPY git_web git_web

CMD hypercorn git_web.main:app --bind '0.0.0.0:8000' --workers "$WORKERS"
