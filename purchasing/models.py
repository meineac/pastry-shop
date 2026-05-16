from django.db import models
from core.models import TimestampedModel
from users.models import CustomerProfile
from catalog.models import Product

class PickupPoint(TimestampedModel):
    address = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255)

    def __str__(self):
        return self.address

class PromoCode(TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    code = models.CharField(max_length=50, unique=True)
    expiration_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    conditions_of_application = models.TextField()

    def __str__(self):
        return self.code

class Order(TimestampedModel):
    class DeliveryType(models.TextChoices):
        COURIER = 'COURIER', 'Courier'
        PICKUP = 'PICKUP', 'Pickup'

    class PaymentType(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Card'

    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    client = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='orders')
    delivery_type = models.CharField(max_length=10, choices=DeliveryType.choices)
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    payment_type = models.CharField(max_length=10, choices=PaymentType.choices)
    status = models.CharField(max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    def __str__(self):
        return f"Order #{self.id} by {self.client.name}"

class OrderItem(TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

class Cart(TimestampedModel):
    client = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"Cart of {self.client.name}"

class CartItem(TimestampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart of {self.cart.client.name}"
