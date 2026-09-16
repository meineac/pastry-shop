"""
Management command: seed_orders

Seeds the database with completed orders and order items.

Prerequisites:
    - seed_users      (customer profiles must exist)
    - seed_catalog    (products must exist)
    - seed_purchasing (pickup points must exist)

Run with:
    python manage.py seed_orders
"""

import logging
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import Product
from purchasing.models import Order, OrderItem, PickupPoint
from users.models import CustomerProfile

logger = logging.getLogger(__name__)

ORDERS_PER_CUSTOMER = 10


class Command(BaseCommand):
    help = (
        "Seed orders. Requires seed_users, seed_catalog, "
        "and seed_purchasing to have been run first."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        products = list(Product.objects.all())
        if not products:
            raise CommandError(
                "No products found. Run 'seed_catalog' first."
            )

        pickup_points = list(PickupPoint.objects.all())
        if not pickup_points:
            raise CommandError(
                "No pickup points found. Run 'seed_purchasing' first."
            )

        profiles = CustomerProfile.objects.select_related("user").all()
        if not profiles.exists():
            raise CommandError(
                "No customer profiles found. Run 'seed_users' first."
            )

        self.stdout.write("Seeding orders...")
        order_count = 0

        for profile in profiles:
            # Skip if this customer already has orders (idempotency)
            if Order.objects.filter(client=profile).exists():
                continue

            for _ in range(ORDERS_PER_CUSTOMER):
                order = Order.objects.create(
                    client=profile,
                    delivery_type=Order.DeliveryType.PICKUP,
                    pickup_point=random.choice(pickup_points),
                    payment_type=Order.PaymentType.CARD,
                    status=Order.OrderStatus.COMPLETED,
                    final_price=0,
                )

                num_items = random.randint(1, 3)
                selected_products = random.sample(products, num_items)
                total_price = Decimal(0)

                for prod in selected_products:
                    qty = random.randint(1, 4)
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        quantity=qty,
                        purchase_price=prod.price,
                        historical_product_name=prod.name,
                    )
                    total_price += prod.price * qty

                order.final_price = total_price
                # Backdate the order artificially
                order.created_at = timezone.now() - timedelta(
                    days=random.randint(1, 365)
                )
                order.save()
                order_count += 1

        self.stdout.write(f"  Orders created: {order_count}")
        self.stdout.write(self.style.SUCCESS("Orders seeded successfully!"))
