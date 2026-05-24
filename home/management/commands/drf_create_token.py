from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    help = "Create a DRF API token for a user."

    def add_arguments(self, parser):
        parser.add_argument(
            "username", type=str, help="Username to create or regenerate token for."
        )

        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing token and create a new one.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        reset = options["reset"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"User '{username}' does not exist."))
            return

        if reset:
            Token.objects.filter(user=user).delete()
            self.stdout.write(self.style.WARNING(f"Deleted existing token for '{username}'."))

        token, created = Token.objects.get_or_create(user=user)
        status = "Created" if created else "Existing"
        self.stdout.write(self.style.SUCCESS(f"{status} token for '{username}': {token.key}"))
