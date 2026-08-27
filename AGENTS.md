# AGENTS.md — Blog

## What this repo is

Personal Wagtail blog, single-node k3s deployment at `blog.evillab.tech`. No CI, no staging, no tests. Verification = `ruff check` + manual click-through.

## Developer commands

```bash
# Install deps and create venv
uv sync

# Run server
uv run manage.py runserver

# Lint / format (only verification we have)
uv run ruff check .
uv run ruff format .

# After any model change — always generate migrations
uv run manage.py makemigrations
uv run manage.py migrate

# Wagtail-specific
uv run manage.py createsuperuser
uv run manage.py collectstatic --noinput
uv run manage.py drf_create_token <username>   # generate API token
```

## Architecture

- **Wagtail 8.0** + **Django 6.0** + **SQLite WAL** (`data/db.sqlite3`)
- **uv** for packages, **ruff** for lint/format (line-length 100, double quotes, spaces)
- **Whitenoise** for static files, **S3 (RustFS)** for media uploads
- **DRF** + token auth for legacy custom API; **Wagtail API v2** for pages/images;
  **Wagtail API v3 preview** for CMS automation

### Page tree

- `HomePage` (root, max 1) → intro + latest posts
- `BlogIndexPage` → lists posts, child of HomePage
- `BlogPage` → date, intro, author (Elder.Evil/Nyx), StreamField body

### Custom API (`/api/blog/`)

- `GET /api/blog/?author=` — list live posts, filter by author
- `POST /api/blog/` — create post (TokenAuthentication required)
- Serializer fields: `title`, `slug`, `date`, `intro`, `body`, `live`, `author`
- Wagtail API v2 at `/api/v2/` for pages + images
- Wagtail API v3 preview at `/api/v3-preview/` for Hermes publishing; see
  `docs/hermes-publishing.md`

## Style & conventions

- **ruff** config lives in `pyproject.toml`. Migrations excluded from lint.
- No type checker, no test suite. Keep changes small and verify by running the server.
- Templates use Wagtail's `{% pageurl %}` and `{% image %}` tags.
- CSS is inline in `blog_site/templates/base.html` — no build step.
- Dark/light theme toggle persists in `localStorage`.

## Deploy

1. Build image: `docker build -t elerevil/blog:latest .`
2. Push, then `kubectl set image` on the Hetzner node
3. Run migrations via Job or `kubectl exec` into the deployment

See `k8s/apply.sh` and `k8s/` manifests. Secrets live in `k8s/secret.yaml` (not committed).

## Environment

Copy `.env.example` to `.env` for local dev. Key vars:

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL` — required for image uploads to work
- `DATABASE_DIR` — SQLite location (default `./data`)

## Gotchas

- **No automated tests.** If you change models or API logic, test manually via the admin and API.
- **Migrations are not auto-checked in CI.** Run `makemigrations` locally after every model change.
- **Static files are collected at Docker build time.** If you add static assets, rebuild the image.
- **S3 media storage fails silently without env vars.** Image uploads will error if `AWS_*` vars are missing.
- **Flat URLs.** Posts live at `/<slug>/`, not `/blog/<slug>/`. Slug collisions across the whole site.
- **Wagtail time zone is `Europe/Helsinki`.** Keep `TIME_ZONE` and `WAGTAIL_TIME_ZONE` in sync.
