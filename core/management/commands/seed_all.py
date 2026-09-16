"""
Management command: seed_all

Orchestrator that runs all seed commands in the correct dependency order.
Replaces the old ``populate_db`` command and standalone ``link_images.py``.

Run with:
    python manage.py seed_all
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand

# Execution order respects the dependency graph:
#   Tier 0 (no deps):  seed_users, seed_catalog, seed_cms, seed_purchasing
#   Tier 1 (needs T0):  seed_reviews
#   Tier 2 (needs T0):  seed_orders
SEED_COMMANDS = [
    "seed_users",
    "seed_catalog",
    "seed_cms",
    "seed_purchasing",
    "seed_reviews",
    "seed_orders",
]


class Command(BaseCommand):
    help = (
        "Run all seed commands in dependency order. "
        "Equivalent to the old populate_db + link_images.py."
    )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING("Running all seed commands...")
        )

        for cmd in SEED_COMMANDS:
            self.stdout.write(self.style.MIGRATE_LABEL(f"\n>>> {cmd}"))
            call_command(cmd, stdout=self.stdout, stderr=self.stderr)

        self.stdout.write(
            self.style.SUCCESS(
                "\nAll seed commands completed successfully!"
            )
        )
