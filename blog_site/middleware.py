from django.http import HttpRequest, HttpResponse


class LegacyAPIDeprecationMiddleware:
    """Advertise the Wagtail v3 preview as the successor to legacy API routes."""

    legacy_prefixes = ("/api/v2/", "/api/blog/", "/api/images/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if request.path.startswith(self.legacy_prefixes):
            response["Deprecation"] = "true"
            response["Link"] = '</api/v3-preview/docs/>; rel="successor-version"'
        return response
