from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.images import get_image_model

Image = get_image_model()


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "title", "file", "width", "height"]
        read_only_fields = ["id", "width", "height"]

    def create(self, validated_data):
        image = Image(**validated_data)
        image.file.save(validated_data["file"].name, validated_data["file"], save=True)
        return image


class ImageUploadView(APIView):
    """POST /api/images/ — upload an image to Wagtail's image library (RustFS S3)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save()
        return Response(
            {
                "id": image.id,
                "title": image.title,
                "width": image.width,
                "height": image.height,
                "download_url": image.file.url,
            },
            status=status.HTTP_201_CREATED,
        )
