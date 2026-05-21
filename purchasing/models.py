from django.db import models
from core.models import TimestampedModel
from users.models import CustomerProfile
from catalog.models import Product

class PickupPoint(TimestampedModel):
    address = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.address} (${self.price})"

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
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Discount as a percentage, e.g. 20 for 20% off."
    )
    minimum_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Minimum cart subtotal required to apply this promo code."
    )
    conditions_of_application = models.TextField(
        help_text="Human-readable description of this promo code's conditions (for display only)."
    )
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.code

class Order(TimestampedModel):
    class PaymentType(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Card'

    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        READY = 'READY', 'Ready'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class DeliveryType(models.TextChoices):
        PICKUP = 'PICKUP', 'Pickup'
        COURIER = 'COURIER', 'Courier'

    client = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='orders')
    delivery_type = models.CharField(max_length=10, choices=DeliveryType.choices, default=DeliveryType.PICKUP)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    payment_type = models.CharField(max_length=10, choices=PaymentType.choices)
    status = models.CharField(max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.client}"

class OrderItem(TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    historical_product_name = models.CharField(max_length=255, default="")

    def get_total(self):
        return self.purchase_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.historical_product_name} in Order #{self.order.id}"

class Cart(TimestampedModel):
    client = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"Cart of {self.client}"

class CartItem(TimestampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        product_name = self.product.name if self.product else "Unavailable Item"
        return f"{self.quantity} x {product_name} in Cart of {self.cart.client}"
