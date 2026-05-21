"""
Checkout service layer.

Business rules that were previously spread across checkout_view and
place_order_view are now isolated here so views stay thin and logic is
reusable and testable in isolation.
"""
import decimal

from django.db import transaction

from .models import Cart, Order, OrderItem, PickupPoint, PromoCode


COURIER_DELIVERY_PRICE = decimal.Decimal('5.00')

# Promo code helpers

def apply_promo_code(promo: PromoCode, subtotal: decimal.Decimal) -> tuple:
    """
    Validate a promo code against the given subtotal and return the discount.

    Returns:
        (is_valid: bool, error_message: str, discount_amount: Decimal)
    """
    min_purchase = promo.minimum_purchase_amount
    discount_percent = promo.discount_percentage

    if subtotal < min_purchase:
        error = f"This promo code requires a minimum purchase of ${min_purchase:.2f}."
        return False, error, decimal.Decimal('0.00')

    discount_amount = (
        subtotal * (discount_percent / decimal.Decimal('100'))
    ).quantize(decimal.Decimal('0.01'))
    return True, '', discount_amount


# Delivery pricing

def calculate_delivery_price(
    delivery_type: str,
    pickup_point: PickupPoint | None,
) -> decimal.Decimal:
    """Return the delivery cost for the given delivery configuration."""
    if delivery_type == Order.DeliveryType.PICKUP:
        return pickup_point.price if pickup_point else decimal.Decimal('0.00')
    return COURIER_DELIVERY_PRICE


def calculate_total(
    subtotal: decimal.Decimal,
    discount: decimal.Decimal,
    delivery_price: decimal.Decimal,
) -> decimal.Decimal:
    """Compute the final order total, floored at zero."""
    total = subtotal - discount + delivery_price
    return max(total, decimal.Decimal('0.00'))


# Cart helpers

def get_cart_subtotal(items) -> decimal.Decimal:
    """Sum price × quantity for all active cart items."""
    return sum(
        item.product.price * item.quantity
        for item in items
        if item.product
    )


# Order placement

def place_order(
    customer_profile,
    cart: Cart,
    delivery_type: str,
    delivery_address: str | None,
    pickup_point: PickupPoint | None,
    payment_type: str,
    promo_code: PromoCode | None,
) -> Order:
    """
    Create an Order from the customer's cart, deduct stock, and clear the cart.

    Must be called inside a database transaction by the caller.
    """
    items = cart.items.select_related('product').all()
    subtotal = get_cart_subtotal(items)

    discount = decimal.Decimal('0.00')
    if promo_code:
        is_valid, _, discount = apply_promo_code(promo_code, subtotal)
        if not is_valid:
            promo_code = None
            discount = decimal.Decimal('0.00')

    delivery_price = calculate_delivery_price(delivery_type, pickup_point)
    final_price = calculate_total(subtotal, discount, delivery_price)

    with transaction.atomic():
        order = Order.objects.create(
            client=customer_profile,
            delivery_type=delivery_type,
            delivery_address=delivery_address,
            delivery_price=delivery_price,
            pickup_point=pickup_point,
            payment_type=payment_type,
            status=Order.OrderStatus.PENDING,
            promo_code=promo_code,
            final_price=final_price,
        )

        for item in items:
            if not item.product:
                continue
            product = item.product
            product.quantity = max(0, product.quantity - item.quantity)
            product.save(update_fields=['quantity'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                purchase_price=product.price,
                historical_product_name=product.name,
            )

        items.delete()

    return order
