from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.api.v2.views import ImagesAPIViewSet

from home.api import BlogPageAPIViewSet
from search.views import search

wagtail_api_router = WagtailAPIRouter("wagtailapi")
wagtail_api_router.register_endpoint("pages", PagesAPIViewSet)
wagtail_api_router.register_endpoint("images", ImagesAPIViewSet)

drf_router = DefaultRouter()
drf_router.register("blog", BlogPageAPIViewSet, basename="blog")

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search, name="search"),
    path(
        "api/v2/",
        include((wagtail_api_router.get_urlpatterns(), "wagtailapi"), namespace="wagtailapi"),
    ),
    path("api/", include(drf_router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("", include(wagtail_urls)),
]
