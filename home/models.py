from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from home.blocks import BodyBlock


class HomePage(Page):
    intro = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [FieldPanel("intro")]

    subpage_types = ["home.BlogPage", "home.BlogIndexPage"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["posts"] = BlogPage.objects.child_of(self).live().order_by("-date")
        return context


class BlogIndexPage(Page):
    intro = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [FieldPanel("intro")]

    subpage_types = ["home.BlogPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["posts"] = BlogPage.objects.child_of(self).live().order_by("-date")
        return context


class BlogPage(Page):
    AUTHOR_CHOICES = [
        ("Elder.Evil", "Elder.Evil"),
        ("Nyx", "Nyx"),
    ]

    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField(BodyBlock(), blank=True, use_json_field=True)
    author = models.CharField(
        max_length=20,
        choices=AUTHOR_CHOICES,
        default="Elder.Evil",
    )

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("author"),
    ]

    parent_page_types = ["home.HomePage", "home.BlogIndexPage"]
    subpage_types = []
