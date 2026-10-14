"""
Management command: seed_purchasing

Seeds the database with pickup points and promo codes.

Run with:
    python manage.py seed_purchasing
"""

import logging
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from purchasing.models import PickupPoint, PromoCode
from core.management.seed_data.purchasing import PICKUP_POINTS_DATA

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed purchasing: pickup points and promo codes."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_pickup_points()
        self._seed_promocodes()
        self.stdout.write(
            self.style.SUCCESS("Purchasing data seeded successfully!")
        )

    # ------------------------------------------------------------------
    # Pickup Points
    # ------------------------------------------------------------------

    def _seed_pickup_points(self):
        self.stdout.write("Seeding pickup points...")
        for data in PICKUP_POINTS_DATA:
            PickupPoint.objects.get_or_create(
                address=data["address"],
                defaults={
                    "working_hours": data["working_hours"],
                    "price": data["price"],
                },
            )

    # ------------------------------------------------------------------
    # Promo Codes
    # ------------------------------------------------------------------

    def _seed_promocodes(self):
        self.stdout.write("Seeding promo codes...")
        for i in range(1, 11):
            code = f"PROMO{i * 10}"
            if i <= 5:
                status = PromoCode.Status.ACTIVE
                exp_date = date.today() + timedelta(days=30 * i)
                conditions = f"Valid for orders over minimum amount. Active code #{i}."
            else:
                status = PromoCode.Status.ARCHIVED
                exp_date = date.today() - timedelta(days=15 * (i - 5))
                conditions = f"Seasonal campaign concluded on {exp_date.strftime('%d/%m/%Y')}."

            PromoCode.objects.update_or_create(
                code=code,
                defaults={
                    "expiration_date": exp_date,
                    "status": status,
                    "discount_percentage": Decimal(5 + (i * 2)),
                    "minimum_purchase_amount": Decimal(10 + (i * 5)),
                    "conditions_of_application": conditions,
                    "is_hidden": False,
                },
            )
