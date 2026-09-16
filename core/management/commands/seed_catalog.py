"""
Management command: seed_catalog

Seeds the database with categories, manufacturers, and products.
Links product images from media/products/ automatically.

Run with:
    python manage.py seed_catalog
"""

import logging
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Manufacturer, Product
from core.management.seed_data.catalog import (
    CATEGORIES,
    MANUFACTURERS,
    PRODUCTS_MD,
)
from core.management.seed_data.images import link_product_images

logger = logging.getLogger(__name__)

UNIT_MAP = {
    "piece": Product.UnitMeasurement.PIECES,
    "kg": Product.UnitMeasurement.KILOGRAMS,
    "liter": Product.UnitMeasurement.LITERS,
}


class Command(BaseCommand):
    help = "Seed catalog: categories, manufacturers, products (with images)."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_manufacturers()
        self._seed_categories()
        count = self._seed_products()
        self.stdout.write(f"  Products created/found: {count}")

        self.stdout.write("Linking product images...")
        link_product_images(self.stdout)

        self.stdout.write(self.style.SUCCESS("Catalog seeded successfully!"))

    # ------------------------------------------------------------------
    # Manufacturers
    # ------------------------------------------------------------------

    def _seed_manufacturers(self):
        self.stdout.write("Seeding manufacturers...")
        for data in MANUFACTURERS:
            Manufacturer.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "contact_email": data["contact_email"],
                },
            )

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def _seed_categories(self):
        self.stdout.write("Seeding categories...")
        for data in CATEGORIES:
            Category.objects.get_or_create(
                name=data["name"],
                defaults={"description": data["description"]},
            )

    # ------------------------------------------------------------------
    # Products (parsed from embedded markdown table)
    # ------------------------------------------------------------------

    def _seed_products(self):
        self.stdout.write("Seeding products...")
        current_category = None
        count = 0

        for line in PRODUCTS_MD.splitlines():
            line = line.strip()
            if not line:
                continue

            cat_match = re.match(r"### \d+\.\s+(.*)", line)
            if cat_match:
                category_name = cat_match.group(1).strip()
                try:
                    current_category = Category.objects.get(name=category_name)
                except Category.DoesNotExist:
                    current_category = None
                continue

            if (
                line.startswith("|")
                and not line.startswith("| ---")
                and not line.startswith("| Product Name")
            ):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) != 5:
                    continue
                name, manufacturer_name, price, unit_str, ingredients = parts
                manufacturer_name = manufacturer_name.replace("**", "")
                price = price.replace("$", "")

                try:
                    manufacturer = Manufacturer.objects.get(
                        name=manufacturer_name
                    )
                except Manufacturer.DoesNotExist:
                    continue

                unit = UNIT_MAP.get(unit_str, Product.UnitMeasurement.PIECES)
                Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "price": price,
                        "quantity": 100,
                        "unit_of_measurement": unit,
                        "ingredients": ingredients,
                        "category": current_category,
                        "manufacturer": manufacturer,
                        "is_active": True,
                    },
                )
                count += 1

        return count
