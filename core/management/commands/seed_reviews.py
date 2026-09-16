"""
Management command: seed_reviews

Seeds the database with customer reviews.

Prerequisites:
    - seed_users (customer users must exist)

Run with:
    python manage.py seed_reviews
"""

import logging
import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cms.models import Review
from users.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed reviews. Requires seed_users to have been run first."

    @transaction.atomic
    def handle(self, *args, **options):
        customers = User.objects.filter(role=User.Role.CUSTOMER)
        if not customers.exists():
            raise CommandError(
                "No customer users found. Run 'seed_users' first."
            )

        self.stdout.write("Seeding reviews...")
        created_count = 0

        for user in customers:
            _, created = Review.objects.get_or_create(
                author=user,
                product=None,
                defaults={
                    "rating": random.randint(4, 5),
                    "review_text": (
                        "Amazing pastry shop! I come here all the time."
                    ),
                },
            )
            if created:
                created_count += 1

        self.stdout.write(f"  Reviews created: {created_count}")
        self.stdout.write(self.style.SUCCESS("Reviews seeded successfully!"))
