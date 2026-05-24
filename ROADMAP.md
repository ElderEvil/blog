# Roadmap

## Now — style, pre-commit, Makefile

### 1. Move CSS to static file + add Prism.js
**Biggest visual impact with zero complexity.**

- Move inline `<style>` from `base.html` to `blog_site/static/css/main.css`
- Add Prism.js (2 files: CSS + JS) for code block syntax highlighting
- Add `language-*` classes to code blocks in `blocks/code.html`
- Prism's dark themes match the existing palette, no color conflicts

**Why not Tailwind / DaisyUI:**
- Requires Node.js build pipeline in the Docker image
- DaisyUI components are designed for apps, not content sites
- Current 150 lines of CSS already handles dark/light toggle, responsive layout, typography
- Adding Tailwind would mean 5+ config files, PostCSS, and CDN deps for the same result

### 2. Pre-commit hooks
**15 minutes, prevents footguns.**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
      - id: django-migrations-check
        name: django migrations check
        entry: uv run manage.py makemigrations --check --dry-run
        language: system
        types: [python]
        pass_filenames: false
```

That's it. Three hooks, all fast, all local. No mypy, no bandit, no 15-hook chains.

### 3. Makefile
**20 minutes. Turns 5 manual steps into `make deploy`.**

```makefile
build:
    docker build -t elerevil/blog:latest .

push: build
    docker push elerevil/blog:latest

deploy: push
    # Apply manifests
    # Run migration job
    # Run createsuperuser job
    # Run sample content job
```

After the GitHub Actions pipeline is set up, the Makefile reduces to local testing commands.

---

## Next — Nyx / Hermes Agent Integration

### 4. Hermes skill for blog posting
**20 minutes. Let Nyx publish directly from Telegram/Discord.**

- Create `~/.hermes/skills/blog-posting/SKILL.md` on Hetzner
- Document the API endpoint: `POST /api/blog/`
- Auth via `Authorization: Token <BLOG_API_TOKEN>`
- Include example payloads with `title`, `slug`, `date`, `intro`, `body`, `author`
- Nyx can then write: `hermes blog create-post "Title" "Intro"`

---

## Later — CI/CD

### 7. GitHub Actions: build + push on tags
**30 minutes. No automated k8s deployment — intentional.**

```yaml
# .github/workflows/build.yml
on:
  push:
    tags: ['v*']
jobs:
  build:
    steps:
      - checkout
      - docker build + tag with version
      - push to Docker Hub (elerevil/blog:$VERSION + latest)
```

**What to skip:**
- No automated k8s deploy. Single-node Hetzner, `kubectl set image` by hand is sufficient.
- No staging environment. One blog. Test locally, deploy manually.
- No ArgoCD / Flux — overkill for one node.

---

## Later — when the need arises

### 5. Media storage → RustFS S3
**~1 hour. Already running RustFS on the cluster at `s3.evillab.tech`.**

- Add `django-storages` with S3 backend
- Configure `DEFAULT_FILE_STORAGE` in settings
- Media files go to S3 instead of PVC
- Zero change to the Docker image — just env vars

### 6. Wagtail search backend
**Only if SQLite WAL becomes a bottleneck.**

- SQLite FTS works for <10,000 posts
- If search slows down, switch to PostgreSQL (already running on the cluster for fallout)
- Wagtail supports PostgreSQL full-text search natively — one setting change

### 7. Blog sections / categories
**When you have enough posts to organize.**

- `BlogIndexPage` model already exists as an optional subpage type
- Tags via `django-taggit` (already installed)
- Add a tag field to `BlogPage` and a tag cloud template

---

## Don't — unless circumstances change

### OAuth / SSO
**Skip. Django admin + strong password is sufficient.**

- Blog has 1-3 authors, you're one of them
- Game players ≠ blog authors — separate identity domains
- If user-facing features need login later (comments?), use Giscus (GitHub Discussions-based, zero backend) instead of building auth
- If SSO becomes necessary, `django-allauth` with GitHub provider is 30 minutes

### Automated k8s deployment
**Skip. Overkill for one node.**

- ArgoCD, Flux, Helm — great tools for multi-node clusters
- For a single-node blog, `kubectl set image` + k8s Jobs for migrate is the right level

### Tailwind / DaisyUI
**Skip. Wrong tool for a content blog.**

- Adds Node.js build step to Docker image
- Component libraries target app UIs, not blog typography
- Current CSS custom properties approach scales cleanly with `{% include %}` partials

---

## Done

- [x] Wagtail 7.4 + Django 6.0 + SQLite WAL
- [x] Whitenoise static files
- [x] Docker build with uv, multi-stage cache
- [x] Flat URLs (no `/blog/` prefix)
- [x] Dark theme toggle, persisted in localStorage
- [x] k3s deployment manifests (Traefik TLS, Let's Encrypt)
- [x] `create_sample_content` management command
- [x] Landing page updated with blog link
- [x] S3 media storage via RustFS (blog-media bucket)
- [x] Umami analytics tracking on blog
- [x] Umami GeoIP database fix (init container downloads GeoLite2-City.mmdb)
- [x] Image uploads + renditions working end-to-end on S3
- [x] Wagtail API v2 + DRF token auth for blog posts
- [x] Author field on `BlogPage` (model, serializer, templates)
- [x] API list endpoint with author filtering (`GET /api/blog/?author=`)
