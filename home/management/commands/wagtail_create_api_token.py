from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from wagtail.models import APIToken


class Command(BaseCommand):
    help = "Create a Wagtail API v3 bearer token for a user."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--name", default="Hermes publisher")

    def handle(self, *args, **options):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=options["username"])
        except user_model.DoesNotExist as error:
            raise CommandError(f"User '{options['username']}' does not exist.") from error

        _, token = APIToken.create_token(user=user, name=options["name"])
        self.stdout.write(self.style.SUCCESS(token))
        self.stderr.write("Store this token securely now; it cannot be displayed again.")
