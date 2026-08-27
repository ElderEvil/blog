# Hermes publishing API

Hermes publishes through Wagtail API v3 at `https://blog.evillab.tech/api/v3-preview/`.
The existing `/api/v2/` and `/api/` interfaces remain available for compatibility.

## Deprecated endpoints

`/api/v2/`, `/api/blog/`, and `/api/images/` are deprecated in favour of v3. Responses from
those paths include `Deprecation: true` and a `Link` header pointing to the v3 interactive docs.
New Hermes integrations must use v3; no removal date has been set yet.

## One-time setup

Create a dedicated non-superuser Wagtail user named `hermes`, and give it **add**, **change**,
and **publish** permission for `BlogPage` beneath the site’s `BlogIndexPage`. On the Hetzner
node, generate a bearer token:

```bash
kubectl -n blog exec deploy/blog -- uv run manage.py wagtail_create_api_token hermes
```

Save the printed value in Hermes’ secret store. It is only shown once. Tokens can be revoked in
Wagtail admin under **Settings → API tokens**.

## Discover before publishing

The API provides its current schema and interactive docs, so Hermes does not need hard-coded
field definitions:

- `GET /api/v3-preview/openapi.json`
- `GET /api/v3-preview/docs/`
- `GET /api/v3-preview/schema/home.BlogPage/` (authenticated)

Find the blog index ID once with `GET /api/v3-preview/pages/?type=home.BlogIndexPage`, then
keep it in Hermes configuration as `BLOG_INDEX_PAGE_ID`.

## Publish a post

Use the generated schema as the source of truth. A typical request is:

```bash
curl --fail-with-body \
  -H "Authorization: Bearer $HERMES_WAGTAIL_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "https://blog.evillab.tech/api/v3-preview/pages/" \
  --data @- <<'JSON'
{
  "title": "Post title",
  "slug": "post-title",
  "date": "2026-08-27",
  "intro": "A short summary.",
  "author": "Elder.Evil",
  "body": [
    {"type": "heading", "value": "Heading"},
    {"type": "paragraph", "value": "<p>Post content.</p>"}
  ],
  "meta": {
    "type": "home.BlogPage",
    "parent_id": 123,
    "action": "publish"
  }
}
JSON
```

Replace `123` with `BLOG_INDEX_PAGE_ID`. Omit `meta.action` to create a draft. Validation and
permission failures are returned as RFC 7807 `application/problem+json` responses.
