from django.http import HttpResponse
from django.test import RequestFactory

from blog_site.middleware import LegacyAPIDeprecationMiddleware


def test_legacy_api_routes_advertise_the_v3_successor():
    middleware = LegacyAPIDeprecationMiddleware(lambda request: HttpResponse())

    response = middleware(RequestFactory().get("/api/blog/"))

    assert response["Deprecation"] == "true"
    assert response["Link"] == '</api/v3-preview/docs/>; rel="successor-version"'


def test_v3_routes_are_not_marked_deprecated():
    middleware = LegacyAPIDeprecationMiddleware(lambda request: HttpResponse())

    response = middleware(RequestFactory().get("/api/v3-preview/pages/"))

    assert "Deprecation" not in response
