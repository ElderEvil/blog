from wagtail.api.v3.urls import api


def test_blog_page_create_schema_exposes_hermes_fields():
    schema = api.get_openapi_schema()
    blog_page = schema["components"]["schemas"]["BlogPageCreateSchema"]

    assert {"date", "intro", "body", "author"} <= blog_page["properties"].keys()
    assert "/api/v3-preview/pages/" in schema["paths"]
