from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from users.decorators import role_required
from users.models import User
from .models import Cart, CartItem, Order, OrderItem, PickupPoint, PromoCode
from .services import (
    COURIER_DELIVERY_PRICE,
    apply_promo_code,
    calculate_delivery_price,
    calculate_total,
    get_cart_subtotal,
    place_order,
)
from cms.models import Review
from catalog.models import Product
from datetime import date
import decimal


# Cart helpers

def get_or_create_cart(user):
    if not hasattr(user, 'customer_profile'):
        return None
    cart, _ = Cart.objects.get_or_create(client=user.customer_profile)
    return cart


# Cart views

def add_to_cart_view(request, product_id):
    if not request.user.is_authenticated:
        return redirect('register')

    if not hasattr(request.user, 'customer_profile'):
        # Admins and staff have no cart
        return redirect('catalog:product_list')

    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request.user)

    if request.method == 'POST':
        if product.quantity <= 0:
            messages.error(request, f"Sorry, {product.name} is out of stock.")
            return redirect('catalog:product_list')

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if cart_item.quantity < product.quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.warning(request, f"You cannot add more of {product.name}. Only {product.quantity} in stock.")
        return redirect('purchasing:cart')

    return redirect('catalog:product_list')


@login_required
def remove_from_cart_view(request, cart_item_id):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('catalog:product_list')

    if request.method == 'POST':
        cart = get_or_create_cart(request.user)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
        cart_item.delete()

    return redirect('purchasing:cart')


@login_required
def cart_view(request):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('catalog:product_list')

    cart = get_or_create_cart(request.user)
    items = cart.items.all()

    # Auto-purge inactive products
    inactive_items = items.filter(product__is_active=False)
    if inactive_items.exists():
        count = inactive_items.count()
        inactive_items.delete()
        messages.warning(request, f"{count} item(s) in your cart became unavailable and were removed.")

    # Check and adjust quantities based on available stock
    for item in items:
        if item.product and item.quantity > item.product.quantity:
            if item.product.quantity == 0:
                item.delete()
                messages.warning(request, f"{item.product.name} is out of stock and was removed from your cart.")
            else:
                item.quantity = item.product.quantity
                item.save()
                messages.warning(request, f"Quantity for {item.product.name} was reduced to {item.product.quantity} due to stock limits.")

    items = cart.items.all()

    total = get_cart_subtotal(items)
    return render(request, 'purchasing/cart.html', {'items': items, 'total': total})

# Promo code application (standalone endpoint)

@login_required
def apply_promo_view(request):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('catalog:product_list')

    if request.method == 'POST':
        code = request.POST.get('promo_code', '').strip()
        try:
            promo = PromoCode.objects.get(code=code, status=PromoCode.Status.ACTIVE, is_hidden=False)
            if promo.expiration_date >= date.today():
                request.session['promo_code_id'] = promo.id
                request.session['promo_error'] = ''
                request.session['promo_success'] = 'Promo code applied successfully.'
            else:
                request.session['promo_error'] = 'Promo code is expired.'
                request.session.pop('promo_code_id', None)
                request.session.pop('promo_success', None)
        except PromoCode.DoesNotExist:
            request.session['promo_error'] = 'Invalid promo code.'
            request.session.pop('promo_code_id', None)
            request.session.pop('promo_success', None)

    return redirect('purchasing:checkout')


# Checkout view

@login_required
def checkout_view(request):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('catalog:product_list')

    cart = get_or_create_cart(request.user)
    items = cart.items.all()

    # Auto-purge inactive products and redirect back to cart
    inactive_items = items.filter(product__is_active=False)
    if inactive_items.exists():
        inactive_items.delete()
        messages.warning(request, "Some products in your cart became unavailable and were removed.")
        return redirect('purchasing:cart')

    if not items:
        return redirect('purchasing:cart')

    # Check if stock is sufficient
    for item in items:
        if item.product and item.quantity > item.product.quantity:
            messages.error(request, f"Sorry, we only have {item.product.quantity} of {item.product.name} in stock. Please adjust your cart.")
            return redirect('purchasing:cart')

    subtotal = get_cart_subtotal(items)

    # Persist form selections to session on POST
    if request.method == 'POST':
        delivery_type = request.POST.get('delivery_type', 'PICKUP')
        pickup_point_id = request.POST.get('pickup_point')
        delivery_address = request.POST.get('delivery_address', '')
        payment_type = request.POST.get('payment_type', 'CASH')
        promo_code_str = request.POST.get('promo_code', '').strip()

        request.session['delivery_type'] = delivery_type
        request.session['pickup_point_id'] = pickup_point_id
        request.session['delivery_address'] = delivery_address
        request.session['payment_type'] = payment_type

        if promo_code_str:
            try:
                promo = PromoCode.objects.get(
                    code=promo_code_str, status=PromoCode.Status.ACTIVE, is_hidden=False
                )
                if promo.expiration_date >= date.today():
                    request.session['promo_code_id'] = promo.id
                    request.session['promo_error'] = ''
                    request.session['promo_success'] = 'Promo code applied successfully.'
                else:
                    request.session['promo_error'] = 'Promo code is expired.'
                    request.session.pop('promo_code_id', None)
                    request.session.pop('promo_success', None)
            except PromoCode.DoesNotExist:
                request.session['promo_error'] = 'Invalid promo code.'
                request.session.pop('promo_code_id', None)
                request.session.pop('promo_success', None)
        elif 'promo_code' in request.POST and not promo_code_str:
            request.session.pop('promo_code_id', None)
            request.session.pop('promo_error', None)
            request.session.pop('promo_success', None)

    # Restore session state
    delivery_type = request.session.get('delivery_type', 'PICKUP')
    pickup_point_id = request.session.get('pickup_point_id')
    delivery_address = request.session.get('delivery_address', '')
    payment_type = request.session.get('payment_type', 'CASH')
    promo_code_id = request.session.get('promo_code_id')

    promo_error = request.session.pop('promo_error', None)
    promo_success = request.session.pop('promo_success', None)

    promo_code = None
    discount = decimal.Decimal('0.00')

    if promo_code_id:
        try:
            promo_code = PromoCode.objects.get(id=promo_code_id)
            is_valid, err_msg, disc_amt = apply_promo_code(promo_code, subtotal)
            if is_valid:
                discount = disc_amt
                if not promo_success:
                    promo_success = 'Promo code applied successfully.'
            else:
                promo_error = err_msg
                request.session.pop('promo_code_id', None)
                promo_code = None
        except PromoCode.DoesNotExist:
            request.session.pop('promo_code_id', None)

    # Delivery price
    pickup_point = None
    if delivery_type == Order.DeliveryType.PICKUP and pickup_point_id:
        try:
            pickup_point = PickupPoint.objects.get(id=pickup_point_id)
        except PickupPoint.DoesNotExist:
            pass
    delivery_price = calculate_delivery_price(delivery_type, pickup_point)
    total = calculate_total(subtotal, discount, delivery_price)

    context = {
        'items': items,
        'subtotal': subtotal,
        'promo_code': promo_code,
        'promo_error': promo_error,
        'promo_success': promo_success,
        'discount': discount,
        'delivery_type': delivery_type,
        'pickup_point_id': int(pickup_point_id) if pickup_point_id and str(pickup_point_id).isdigit() else None,
        'delivery_address': delivery_address,
        'payment_type': payment_type,
        'delivery_price': delivery_price,
        'total': total,
        'pickup_points': PickupPoint.objects.all(),
    }
    return render(request, 'purchasing/checkout.html', context)


# Order placement view

@login_required
def place_order_view(request):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('catalog:product_list')

    if request.method != 'POST':
        return redirect('purchasing:checkout')

    cart = get_or_create_cart(request.user)
    items = cart.items.all()

    if not items:
        return redirect('purchasing:cart')

    # Purge inactive products before order
    inactive_items = items.filter(product__is_active=False)
    if inactive_items.exists():
        inactive_items.delete()
        request.session['promo_error'] = "Some products in your cart became unavailable and were removed."
        return redirect('purchasing:cart')

    # Check if stock is sufficient
    for item in items:
        if item.product and item.quantity > item.product.quantity:
            messages.error(request, f"Sorry, we only have {item.product.quantity} of {item.product.name} in stock.")
            return redirect('purchasing:cart')

    # Parse and validate delivery details
    delivery_type = request.POST.get('delivery_type', 'PICKUP')
    pickup_point_id = request.POST.get('pickup_point')
    delivery_address = request.POST.get('delivery_address', '').strip()
    payment_type = request.POST.get('payment_type')

    pickup_point = None
    if delivery_type == Order.DeliveryType.PICKUP:
        if not pickup_point_id:
            request.session['promo_error'] = "Please select a store for pickup."
            return redirect('purchasing:checkout')
        pickup_point = get_object_or_404(PickupPoint, id=pickup_point_id)
        delivery_address = None
    else:
        if not delivery_address:
            request.session['promo_error'] = "Please enter an address for courier delivery."
            return redirect('purchasing:checkout')

    if payment_type not in [Order.PaymentType.CASH, Order.PaymentType.CARD]:
        request.session['promo_error'] = "Please select a valid payment method."
        return redirect('purchasing:checkout')

    # Resolve promo code from session
    promo_code = None
    promo_code_id = request.session.get('promo_code_id')
    if promo_code_id:
        try:
            promo_code = PromoCode.objects.get(id=promo_code_id)
        except PromoCode.DoesNotExist:
            pass

    # Delegate all business logic to the service layer
    with transaction.atomic():
        place_order(
            customer_profile=request.user.customer_profile,
            cart=cart,
            delivery_type=delivery_type,
            delivery_address=delivery_address,
            pickup_point=pickup_point,
            payment_type=payment_type,
            promo_code=promo_code,
        )

    # Clear session checkout state
    for key in ('promo_code_id', 'delivery_type', 'pickup_point_id', 'delivery_address', 'payment_type'):
        request.session.pop(key, None)

    return redirect('profile')

# Order history views

@role_required([User.Role.CUSTOMER])
def order_history_view(request):
    profile = getattr(request.user, 'customer_profile', None)
    history_orders = []
    if profile:
        history_orders = profile.orders.filter(
            status__in=[Order.OrderStatus.COMPLETED, Order.OrderStatus.CANCELLED]
        ).order_by('-created_at')
    return render(request, 'purchasing/order_history.html', {'history_orders': history_orders})


@role_required([User.Role.CUSTOMER])
def order_details_view(request, order_id):
    profile = getattr(request.user, 'customer_profile', None)
    order = get_object_or_404(Order, id=order_id, client=profile)
    items = order.items.all()

    reviewed_product_ids = set(
        Review.objects.filter(
            author=request.user,
            product__in=[item.product for item in items if item.product],
        ).values_list('product_id', flat=True)
    )

    for item in items:
        item.already_reviewed = item.product_id in reviewed_product_ids if item.product else False

    return render(request, 'purchasing/order_details.html', {'order': order, 'items': items})
