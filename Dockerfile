FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_DEBUG=false

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
RUN uv run manage.py collectstatic --noinput
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "blog_site.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
