from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from home.models import BlogPage, HomePage


class Command(BaseCommand):
    help = "Create initial site structure and sample blog content"

    def handle(self, **options):
        root = Page.get_first_root_node()

        # -- Site --
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stdout.write("No default site found.")
            return

        # -- HomePage --
        homepage = HomePage.objects.first()
        if not homepage:
            homepage = HomePage(
                title="Home",
                intro="<p>Welcome to the blog.</p>",
            )
            root.add_child(instance=homepage)
            homepage.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created HomePage"))

            site.root_page = homepage
            site.save()
        else:
            self.stdout.write("HomePage already exists, skipping.")

        # -- Sample BlogPage --
        if BlogPage.objects.child_of(homepage).exists():
            self.stdout.write("BlogPage(s) already exist, skipping sample post.")
            return

        sample = BlogPage(
            title="Getting Started",
            date="2026-05-12",
            intro=(
                "A quick tour of what the blog can do — "
                "code blocks, images, embeds, and rich text."
            ),
        )
        sample.body = [
            ("heading", "Hello, World"),
            (
                "paragraph",
                '<p>This blog runs on <b>Wagtail 7.4</b> with <b>Django 6.0</b>, '
                "deployed as a single container on k3s. "
                "Static files are served by Whitenoise, TLS is handled by Traefik, "
                "and the database is SQLite with WAL mode — simple, fast, and boring.</p>",
            ),
            ("heading", "Code Blocks"),
            (
                "paragraph",
                "<p>Inline <code>code</code> works in rich text. "
                "Full blocks use the code StreamField type:</p>",
            ),
            (
                "code",
                {
                    "language": "python",
                    "code": 'def greet(name: str) -> str:\n    return f"Hello, {name}!"\n\n'
                            'if __name__ == "__main__":\n    print(greet("World"))',
                },
            ),
            ("heading", "What's Next"),
            (
                "paragraph",
                "<p>More posts coming soon — infrastructure deep-dives, "
                "Python tooling, k3s adventures, and whatever breaks in production.</p>",
            ),
        ]
        homepage.add_child(instance=sample)
        sample.save_revision().publish()
        self.stdout.write(self.style.SUCCESS("Created sample BlogPage"))
