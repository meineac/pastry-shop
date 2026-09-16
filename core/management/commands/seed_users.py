"""
Management command: seed_users

Seeds the database with user accounts (superuser, staff, customers)
and their associated profiles. Links staff profile photos automatically.

Run with:
    python manage.py seed_users
"""

import logging
import os
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from users.models import User, CustomerProfile, StaffProfile
from core.management.seed_data.images import link_staff_images

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed users: superuser, staff (with photos), and customers."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_superuser()
        self._seed_staff()
        self._seed_customers()
        self.stdout.write(self.style.SUCCESS("Users seeded successfully!"))

    # ------------------------------------------------------------------
    # Superuser
    # ------------------------------------------------------------------

    def _seed_superuser(self):
        su_username = os.environ.get("SUPERUSER_USERNAME", "admin")
        su_email = os.environ.get("SUPERUSER_EMAIL", "admin@example.com")
        su_password = os.environ.get("SUPERUSER_PASSWORD", "adminpass")

        if not User.objects.filter(username=su_username).exists():
            User.objects.create_superuser(
                username=su_username,
                email=su_email,
                password=su_password,
            )
            self.stdout.write(f"  Created superuser '{su_username}'.")
        else:
            self.stdout.write(f"  Superuser '{su_username}' already exists.")

    # ------------------------------------------------------------------
    # Staff
    # ------------------------------------------------------------------

    def _seed_staff(self):
        self.stdout.write("Seeding staff users...")
        created_count = 0

        for i in range(1, 11):
            username = f"staffuser{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"staff{i}@pastry.com",
                    "role": User.Role.STAFF,
                },
            )
            if created:
                user.set_password("staffpass123")
                user.save()
                StaffProfile.objects.create(
                    user=user,
                    position="Pastry Shop Employee",
                    contact_details=f"Phone: +375 (29) 222-22-{i:02d}",
                    date_of_birth=date(1990, 1, 1),
                )
                created_count += 1

        self.stdout.write(f"  Staff users created: {created_count}")
        self.stdout.write("Linking staff photos...")
        link_staff_images(self.stdout)

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    def _seed_customers(self):
        self.stdout.write("Seeding customer users...")
        created_count = 0

        for i in range(1, 21):
            username = f"customer{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"customer{i}@pastry.com",
                    "role": User.Role.CUSTOMER,
                },
            )
            if created:
                user.set_password("customerpass123")
                user.save()
                CustomerProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "date_of_birth": date(1995, 5, 15),
                        "phone_number": f"+375 (29) 111-11-{i:02d}",
                    },
                )
                created_count += 1

        self.stdout.write(f"  Customer users created: {created_count}")
