# Blog

Personal blog powered by [Wagtail](https://wagtail.org/), deployed on k3s at [blog.evillab.tech](https://blog.evillab.tech).

## Stack

- **Python 3.13** + **Django 6.0** + **Wagtail 7.4**
- **uv** for package management, **ruff** for linting/formatting
- **SQLite** (WAL mode) for data, **Whitenoise** for static files in production
- **Docker** + **k3s** (Traefik ingress, cert-manager TLS)

## Local development

```bash
# Install dependencies and create venv
uv sync

# Run migrations
uv run manage.py migrate

# Create admin user
uv run manage.py createsuperuser

# Start dev server
uv run manage.py runserver
```

Open http://localhost:8000/admin to access the Wagtail admin.

### Code quality

```bash
uv run ruff check .     # lint
uv run ruff format .    # format
```

## Page structure

The site uses a Wagtail page tree:

- **HomePage** (1 instance, root) — intro text, links to blog index
- **BlogIndexPage** — lists published blog posts, newest first
- **BlogPage** — individual post with date, intro, and a StreamField body supporting headings, rich text, images, embeds, and code blocks

## Configuration

All settings are driven by environment variables. See `.env.example` for available options.

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | (insecure dev key) | Django secret key |
| `DJANGO_DEBUG` | `true` | Debug mode (set to `false` in prod) |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | Comma-separated origins |
| `WAGTAIL_SITE_NAME` | `My Blog` | Site name in Wagtail admin |
| `WAGTAILADMIN_BASE_URL` | `http://localhost:8000` | Base URL for admin notifications |
| `DATABASE_DIR` | `./data` | SQLite database directory |
| `MEDIA_DIR` | `./data/media` | Uploaded media directory |

## Deployment (k3s)

```bash
# Build and tag the image
docker build -t elerevil/blog:latest .

# Push to your container registry, then update k8s/deployment.yaml image field

# Apply manifests
./k8s/apply.sh

# Post-deploy setup
kubectl -n blog exec deploy/blog -- uv run manage.py migrate
kubectl -n blog exec deploy/blog -- uv run manage.py createsuperuser
```

The k8s setup expects:
- **Traefik** as the ingress controller (default in k3s)
- **cert-manager** with a `letsencrypt-prod` ClusterIssuer for TLS
- A **PersistentVolumeClaim** `blog-data` (10Gi) for SQLite and media files
