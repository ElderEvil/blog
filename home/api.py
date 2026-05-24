from rest_framework import serializers, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from wagtail.models import Site

from home.models import BlogIndexPage, BlogPage


class BlogPageSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=255)
    date = serializers.DateField()
    intro = serializers.CharField(max_length=250)
    body = serializers.JSONField(required=False, default=list)
    live = serializers.BooleanField(default=True)
    author = serializers.ChoiceField(choices=["Elder.Evil", "Nyx"], default="Elder.Evil")
    search_description = serializers.CharField(required=False, default="", allow_blank=True)


class BlogPageUpdateSerializer(serializers.Serializer):
    """All fields optional for PATCH updates."""
    title = serializers.CharField(max_length=255, required=False)
    slug = serializers.SlugField(max_length=255, required=False)
    date = serializers.DateField(required=False)
    intro = serializers.CharField(max_length=250, required=False)
    body = serializers.JSONField(required=False)
    live = serializers.BooleanField(required=False)
    author = serializers.ChoiceField(choices=["Elder.Evil", "Nyx"], required=False)
    search_description = serializers.CharField(required=False, allow_blank=True)


class BlogPageAPIViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = BlogPage.objects.live().order_by("-first_published_at")
        author = request.query_params.get("author")
        if author:
            qs = qs.filter(author=author)
        posts = [
            {
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "date": p.date.isoformat(),
                "intro": p.intro,
                "url": p.url,
                "author": p.author,
                "search_description": p.search_description,
            }
            for p in qs
        ]
        return Response(posts)

    def retrieve(self, request, pk=None):
        try:
            page = BlogPage.objects.get(pk=pk)
        except BlogPage.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "date": page.date.isoformat(),
            "intro": page.intro,
            "body": page.body.raw_data if hasattr(page.body, "raw_data") else [],
            "url": page.url,
            "author": page.author,
            "live": page.live,
            "search_description": page.search_description,
        })

    def create(self, request):
        serializer = BlogPageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Find the parent page — prefer BlogIndexPage, fallback to HomePage
        site = Site.find_for_request(request)
        root_page = site.root_page if site else None

        parent = None
        if root_page:
            parent = BlogIndexPage.objects.child_of(root_page).first()
            if not parent:
                parent = root_page

        if not parent:
            return Response(
                {"detail": "No suitable parent page found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for slug collision
        existing = BlogPage.objects.filter(slug=data["slug"]).first()
        if existing:
            return Response(
                {"detail": f"A page with slug '{data['slug']}' already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        blog_page = BlogPage(
            title=data["title"],
            slug=data["slug"],
            date=data["date"],
            intro=data["intro"],
            body=data.get("body", []),
            live=data.get("live", True),
            author=data.get("author", "Elder.Evil"),
            search_description=data.get("search_description", ""),
        )
        parent.add_child(instance=blog_page)
        blog_page.save_revision().publish()

        return Response(
            {
                "id": blog_page.id,
                "title": blog_page.title,
                "slug": blog_page.slug,
                "url": blog_page.url,
            },
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, pk=None):
        try:
            page = BlogPage.objects.get(pk=pk)
        except BlogPage.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BlogPageUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        for field, value in data.items():
            setattr(page, field, value)

        page.save_revision().publish()

        return Response({
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "url": page.url,
        })
