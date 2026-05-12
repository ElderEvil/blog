from django.shortcuts import render
from wagtail.models import Page


def search(request):
    query = request.GET.get("query", "")
    results = Page.objects.live().search(query) if query else Page.objects.none()

    return render(
        request,
        "search/search.html",
        {"query": query, "results": results},
    )
