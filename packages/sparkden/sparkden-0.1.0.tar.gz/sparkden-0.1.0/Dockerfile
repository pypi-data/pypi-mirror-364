########################################################
# Base image with uv installed
########################################################
FROM python:3.12-slim AS assistants-base
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/
ENV UV_LINK_MODE=copy
WORKDIR /assistants-app


########################################################
# Development image
########################################################
FROM assistants-base AS assistants-dev
# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /assistants-app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

EXPOSE 8000
CMD ["uv", "run", "litestar", "--app-dir", "/assistants-app/src", "run", "--host", "0.0.0.0", "--port", "8000", "-r"]


########################################################
# Production build image
########################################################
FROM assistants-base AS assistants-prod
# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /assistants-app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

EXPOSE 8000
CMD ["uv", "run", "litestar", "--app-dir", "/assistants-app/src", "run", "--host", "0.0.0.0", "--port", "8000"]
