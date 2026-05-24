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


class BlogPageAPIViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
