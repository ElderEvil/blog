"""Tests for blog API serializers (BlogPageSerializer, BlogPageUpdateSerializer).

Tests focus on validation rules — field constraints, choice validation,
optional/required behavior — without a database, since DRF serializers
are plain validation classes.
"""

import pytest

from home.api import BlogPageSerializer, BlogPageUpdateSerializer

# ── BlogPageSerializer (create: all fields required except body/search_description) ──


class TestBlogPageSerializer:
    def test_valid_data(self):
        s = BlogPageSerializer(data={
            "title": "Hello World",
            "slug": "hello-world",
            "date": "2025-01-15",
            "intro": "A brief intro",
        })
        assert s.is_valid(), s.errors
        assert s.validated_data["title"] == "Hello World"
        assert s.validated_data["author"] == "Elder.Evil"  # default

    def test_title_required(self):
        s = BlogPageSerializer(data={"slug": "hi", "date": "2025-01-01", "intro": "x"})
        assert not s.is_valid()
        assert "title" in s.errors

    def test_title_max_length(self):
        s = BlogPageSerializer(data={
            "title": "x" * 256,
            "slug": "hi",
            "date": "2025-01-01",
            "intro": "x",
        })
        assert not s.is_valid()
        assert "title" in s.errors

    def test_slug_required(self):
        s = BlogPageSerializer(data={"title": "Hi", "date": "2025-01-01", "intro": "x"})
        assert not s.is_valid()
        assert "slug" in s.errors

    def test_slug_format_valid(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hello-world-123", "date": "2025-01-01", "intro": "x",
        })
        assert s.is_valid(), s.errors

    def test_slug_format_invalid(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "Hello World!", "date": "2025-01-01", "intro": "x",
        })
        assert not s.is_valid()
        assert "slug" in s.errors

    def test_date_valid_format(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "2025-06-15", "intro": "x",
        })
        assert s.is_valid(), s.errors

    def test_date_invalid_format(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "not-a-date", "intro": "x",
        })
        assert not s.is_valid()
        assert "date" in s.errors

    def test_intro_required(self):
        s = BlogPageSerializer(data={"title": "Hi", "slug": "hi", "date": "2025-01-01"})
        assert not s.is_valid()
        assert "intro" in s.errors

    def test_intro_max_length(self):
        s = BlogPageSerializer(data={
            "title": "Hi",
            "slug": "hi",
            "date": "2025-01-01",
            "intro": "x" * 251,
        })
        assert not s.is_valid()
        assert "intro" in s.errors

    def test_body_default_is_list(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "2025-01-01", "intro": "x",
        })
        assert s.is_valid(), s.errors
        assert s.validated_data["body"] == []

    def test_body_valid_json(self):
        s = BlogPageSerializer(data={
            "title": "Hi",
            "slug": "hi",
            "date": "2025-01-01",
            "intro": "x",
            "body": [{"type": "paragraph", "value": "Hello"}],
        })
        assert s.is_valid(), s.errors

    def test_body_accepts_string(self):
        """JSONField accepts any JSON-encodable value, including strings."""
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "2025-01-01", "intro": "x", "body": "raw text",
        })
        assert s.is_valid(), s.errors

    @pytest.mark.parametrize("author", ["Elder.Evil", "Nyx"])
    def test_valid_authors(self, author):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "2025-01-01", "intro": "x", "author": author,
        })
        assert s.is_valid(), s.errors

    def test_invalid_author(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "2025-01-01", "intro": "x", "author": "Someone",
        })
        assert not s.is_valid()
        assert "author" in s.errors

    def test_live_default_true(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "2025-01-01", "intro": "x",
        })
        assert s.is_valid(), s.errors
        assert s.validated_data["live"] is True

    def test_live_false_explicitly(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "2025-01-01", "intro": "x", "live": False,
        })
        assert s.is_valid(), s.errors
        assert s.validated_data["live"] is False

    def test_search_description_default_empty(self):
        s = BlogPageSerializer(data={
            "title": "Hi", "slug": "hi", "date": "2025-01-01", "intro": "x",
        })
        assert s.is_valid(), s.errors
        assert s.validated_data["search_description"] == ""

    def test_extra_fields_ignored(self):
        s = BlogPageSerializer(data={
            "title": "Hi",
            "slug": "hi",
            "date": "2025-01-01",
            "intro": "x",
            "unknown_field": "should_be_ignored",
        })
        assert s.is_valid(), s.errors
        assert "unknown_field" not in s.validated_data


# ── BlogPageUpdateSerializer (PATCH: all fields optional) ──


class TestBlogPageUpdateSerializer:
    def test_empty_data_is_valid(self):
        s = BlogPageUpdateSerializer(data={}, partial=True)
        assert s.is_valid(), s.errors

    def test_partial_title(self):
        s = BlogPageUpdateSerializer(data={"title": "Updated Title"}, partial=True)
        assert s.is_valid(), s.errors
        assert s.validated_data["title"] == "Updated Title"

    def test_partial_slug(self):
        s = BlogPageUpdateSerializer(data={"slug": "updated-slug"}, partial=True)
        assert s.is_valid(), s.errors
        assert s.validated_data["slug"] == "updated-slug"

    def test_partial_intro(self):
        s = BlogPageUpdateSerializer(data={"intro": "New intro"}, partial=True)
        assert s.is_valid(), s.errors

    def test_partial_date(self):
        s = BlogPageUpdateSerializer(data={"date": "2025-03-01"}, partial=True)
        assert s.is_valid(), s.errors

    def test_partial_live(self):
        s = BlogPageUpdateSerializer(data={"live": False}, partial=True)
        assert s.is_valid(), s.errors
        assert s.validated_data["live"] is False

    def test_partial_author_valid(self):
        s = BlogPageUpdateSerializer(data={"author": "Nyx"}, partial=True)
        assert s.is_valid(), s.errors

    def test_partial_author_invalid(self):
        s = BlogPageUpdateSerializer(data={"author": "Invalid"}, partial=True)
        assert not s.is_valid()
        assert "author" in s.errors

    def test_partial_body(self):
        s = BlogPageUpdateSerializer(data={"body": []}, partial=True)
        assert s.is_valid(), s.errors

    def test_extra_fields_ignored(self):
        s = BlogPageUpdateSerializer(data={"unknown": "x"}, partial=True)
        assert s.is_valid(), s.errors
        assert "unknown" not in s.validated_data

    def test_title_max_length(self):
        s = BlogPageUpdateSerializer(data={"title": "x" * 256}, partial=True)
        assert not s.is_valid()
        assert "title" in s.errors
