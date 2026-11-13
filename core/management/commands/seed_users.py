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

    STAFF_MEMBERS = [
        {
            "username": "staffuser1",
            "first_name": "Claire",
            "last_name": "Bennett",
            "email": "claire.bennett@pastryshop.example.com",
            "position": "Head Pastry Chef",
            "phone": "+375 (29) 111-22-33",
            "dob": date(1988, 4, 12),
            "url": "https://pastryshop.example.com/team/claire_bennett.html",
        },
        {
            "username": "staffuser2",
            "first_name": "Antoine",
            "last_name": "Dubois",
            "email": "antoine.dubois@pastryshop.example.com",
            "position": "Master Chocolatier",
            "phone": "8 (029) 2223344",
            "dob": date(1985, 9, 23),
            "url": "https://pastryshop.example.com/team/antoine_dubois.php",
        },
        {
            "username": "staffuser3",
            "first_name": "Sophie",
            "last_name": "Laurent",
            "email": "sophie.laurent@pastryshop.example.com",
            "position": "Artisan Bread Baker",
            "phone": "+375 (29) 333 44 55",
            "dob": date(1992, 2, 17),
            "url": "https://pastryshop.example.com/team/sophie_laurent.html",
        },
        {
            "username": "staffuser4",
            "first_name": "Mateo",
            "last_name": "Rossi",
            "email": "mateo.rossi@pastryshop.example.com",
            "position": "Viennoiserie Specialist",
            "phone": "80294445566",
            "dob": date(1990, 7, 30),
            "url": "https://pastryshop.example.com/team/mateo_rossi.php",
        },
        {
            "username": "staffuser5",
            "first_name": "Elena",
            "last_name": "Rostova",
            "email": "elena.rostova@pastryshop.example.com",
            "position": "Cake Design Artist",
            "phone": "+375 (29) 555-66-77",
            "dob": date(1993, 11, 5),
            "url": "https://pastryshop.example.com/team/elena_rostova.html",
        },
        {
            "username": "staffuser6",
            "first_name": "Liam",
            "last_name": "Gallagher",
            "email": "liam.gallagher@pastryshop.example.com",
            "position": "Tart & Entremet Chef",
            "phone": "8 (029) 6667788",
            "dob": date(1989, 3, 14),
            "url": "https://pastryshop.example.com/team/liam_gallagher.php",
        },
        {
            "username": "staffuser7",
            "first_name": "Camille",
            "last_name": "Moreau",
            "email": "camille.moreau@pastryshop.example.com",
            "position": "Quality & Recipe Specialist",
            "phone": "+375 (29) 777 88 99",
            "dob": date(1991, 8, 22),
            "url": "https://pastryshop.example.com/team/camille_moreau.html",
        },
        {
            "username": "staffuser8",
            "first_name": "Oliver",
            "last_name": "Schmidt",
            "email": "oliver.schmidt@pastryshop.example.com",
            "position": "Production Manager",
            "phone": "80298889900",
            "dob": date(1986, 12, 1),
            "url": "https://pastryshop.example.com/team/oliver_schmidt.php",
        },
        {
            "username": "staffuser9",
            "first_name": "Hannah",
            "last_name": "Abbott",
            "email": "hannah.abbott@pastryshop.example.com",
            "position": "Head Barista & Sommelier",
            "phone": "+375 (29) 999-00-11",
            "dob": date(1994, 6, 19),
            "url": "https://pastryshop.example.com/team/hannah_abbott.html",
        },
        {
            "username": "staffuser10",
            "first_name": "Noah",
            "last_name": "Dupont",
            "email": "noah.dupont@pastryshop.example.com",
            "position": "Pastry Sous Chef",
            "phone": "8 (029) 1234567",
            "dob": date(1995, 1, 28),
            "url": "https://pastryshop.example.com/team/noah_dupont.php",
        },
    ]

    def _seed_staff(self):
        self.stdout.write("Seeding staff users...")
        created_count = 0

        for member in self.STAFF_MEMBERS:
            user, created = User.objects.get_or_create(
                username=member["username"],
                defaults={
                    "first_name": member["first_name"],
                    "last_name": member["last_name"],
                    "email": member["email"],
                    "role": User.Role.STAFF,
                },
            )
            if not created:
                user.first_name = member["first_name"]
                user.last_name = member["last_name"]
                user.email = member["email"]
                user.save()
            else:
                user.set_password("staffpass123")
                user.save()

            profile, _ = StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    "position": member["position"],
                    "contact_details": member["phone"],
                    "date_of_birth": member["dob"],
                    "url": member["url"],
                },
            )
            profile.position = member["position"]
            profile.contact_details = member["phone"]
            profile.date_of_birth = member["dob"]
            profile.url = member["url"]
            profile.save()

            if created:
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
