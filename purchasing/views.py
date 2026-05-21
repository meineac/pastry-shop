from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from users.decorators import role_required
from users.models import User
from .models import Cart, CartItem, Order, OrderItem, PickupPoint, PromoCode
from catalog.models import Product
from datetime import date
import decimal
import re

def get_or_create_cart(user):
    if not hasattr(user, 'customer_profile'):
        return None
    cart, created = Cart.objects.get_or_create(client=user.customer_profile)
    return cart

def add_to_cart_view(request, product_id):
    if not request.user.is_authenticated:
        return redirect('register')

    if not hasattr(request.user, 'customer_profile'):
        # Admin and staff don't have carts
        return redirect('catalog:product_list')

    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request.user)

    if request.method == 'POST':
        # Add product or increment quantity
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
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

    # Auto-purge inactive products from the cart
    inactive_items = items.filter(product__is_active=False)
    if inactive_items.exists():
        inactive_items_count = inactive_items.count()
        inactive_items.delete()
        messages.warning(request, f"{inactive_items_count} item(s) in your cart became unavailable and were removed.")
        items = cart.items.all()

    total = sum(item.product.price * item.quantity for item in items if item.product)

    context = {
        'items': items,
        'total': total
    }
    return render(request, 'purchasing/cart.html', context)

COURIER_DELIVERY_PRICE = decimal.Decimal('5.00')

def parse_promo_code(promo, subtotal):
    discount_percent = decimal.Decimal('10.00') # Default 10%
    # Extract discount percentage
    pct_match = re.search(r'(\d+)\s*%', promo.conditions_of_application)
    if not pct_match:
        pct_match = re.search(r'(\d+)\s*%', promo.code)
    if not pct_match:
        code_digits = re.search(r'([A-Za-z]+)(\d+)', promo.code)
        if code_digits:
            val = int(code_digits.group(2))
            if 0 < val <= 100:
                discount_percent = decimal.Decimal(val)
    else:
        discount_percent = decimal.Decimal(pct_match.group(1))

    # Extract minimum purchase requirement
    min_purchase = decimal.Decimal('0.00')
    min_match = re.search(r'(?:min|minimum|over|above|least|>\s*)\s*(?:\$)?\s*(\d+(?:\.\d{2})?)', promo.conditions_of_application.lower())
    if min_match:
        min_purchase = decimal.Decimal(min_match.group(1))
    
    is_valid = subtotal >= min_purchase
    error_message = ""
    if not is_valid:
        error_message = f"This promo code requires a minimum purchase of ${min_purchase:.2f}."
        
    discount_amount = (subtotal * (discount_percent / decimal.Decimal('100.00'))).quantize(decimal.Decimal('0.01'))
    return is_valid, error_message, discount_amount

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

@login_required
def checkout_view(request):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('catalog:product_list')

    cart = get_or_create_cart(request.user)
    items = cart.items.all()

    # Auto-purge inactive products from the cart
    inactive_items = items.filter(product__is_active=False)
    if inactive_items.exists():
        inactive_items.delete()
        messages.warning(request, "Some products in your cart became unavailable and were removed.")
        return redirect('purchasing:cart')

    if not items:
        return redirect('purchasing:cart')

    subtotal = sum(item.product.price * item.quantity for item in items if item.product)

    # Check if there is a post to update delivery state
    if request.method == 'POST':
        delivery_type = request.POST.get('delivery_type', 'PICKUP')
        pickup_point_id = request.POST.get('pickup_point')
        delivery_address = request.POST.get('delivery_address', '')
        payment_type = request.POST.get('payment_type', 'CASH')
        promo_code_str = request.POST.get('promo_code', '').strip()

        # Save to session
        request.session['delivery_type'] = delivery_type
        request.session['pickup_point_id'] = pickup_point_id
        request.session['delivery_address'] = delivery_address
        request.session['payment_type'] = payment_type
        
        if promo_code_str:
            try:
                promo = PromoCode.objects.get(code=promo_code_str, status=PromoCode.Status.ACTIVE, is_hidden=False)
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

    # Read state from session
    delivery_type = request.session.get('delivery_type', 'PICKUP')
    pickup_point_id = request.session.get('pickup_point_id')
    delivery_address = request.session.get('delivery_address', '')
    payment_type = request.session.get('payment_type', 'CASH')
    promo_code_id = request.session.get('promo_code_id')

    # Promo code discount calculation
    promo_code = None
    discount = decimal.Decimal('0.00')
    promo_error = request.session.pop('promo_error', None)
    promo_success = request.session.pop('promo_success', None)

    if promo_code_id:
        try:
            promo_code = PromoCode.objects.get(id=promo_code_id)
            is_valid, err_msg, disc_amt = parse_promo_code(promo_code, subtotal)
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

    # Delivery price calculation
    delivery_price = decimal.Decimal('0.00')
    pickup_point = None
    if delivery_type == 'PICKUP':
        if pickup_point_id:
            try:
                pickup_point = PickupPoint.objects.get(id=pickup_point_id)
                delivery_price = pickup_point.price
            except PickupPoint.DoesNotExist:
                pass
    else:
        delivery_price = COURIER_DELIVERY_PRICE

    total = subtotal - discount + delivery_price
    if total < decimal.Decimal('0.00'):
        total = decimal.Decimal('0.00')

    pickup_points = PickupPoint.objects.all()

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
        'pickup_points': pickup_points,
    }
    return render(request, 'purchasing/checkout.html', context)

@login_required
def place_order_view(request):
    if not hasattr(request.user, 'customer_profile'):
        return redirect('catalog:product_list')

    if request.method == 'POST':
        cart = get_or_create_cart(request.user)
        items = cart.items.all()

        if not items:
            return redirect('purchasing:cart')

        # Check for inactive products in cart
        inactive_items = items.filter(product__is_active=False)
        if inactive_items.exists():
            inactive_items.delete()
            request.session['promo_error'] = "Some products in your cart became unavailable and were removed."
            return redirect('purchasing:cart')

        # Read POST details
        delivery_type = request.POST.get('delivery_type', 'PICKUP')
        pickup_point_id = request.POST.get('pickup_point')
        delivery_address = request.POST.get('delivery_address', '').strip()
        payment_type = request.POST.get('payment_type')

        # Validate delivery fields
        pickup_point = None
        delivery_price = decimal.Decimal('0.00')
        if delivery_type == 'PICKUP':
            if not pickup_point_id:
                request.session['promo_error'] = "Please select a store for pickup."
                return redirect('purchasing:checkout')
            pickup_point = get_object_or_404(PickupPoint, id=pickup_point_id)
            delivery_price = pickup_point.price
            delivery_address = None
        else:
            if not delivery_address:
                request.session['promo_error'] = "Please enter an address for courier delivery."
                return redirect('purchasing:checkout')
            delivery_price = COURIER_DELIVERY_PRICE
            pickup_point = None

        if payment_type not in [Order.PaymentType.CASH, Order.PaymentType.CARD]:
            request.session['promo_error'] = "Please select a valid payment method."
            return redirect('purchasing:checkout')

        # Calculate pricing
        subtotal = sum(item.product.price * item.quantity for item in items if item.product)

        # Handle PromoCode
        promo_code_id = request.session.get('promo_code_id')
        promo_code = None
        discount = decimal.Decimal('0.00')

        if promo_code_id:
            try:
                promo_code = PromoCode.objects.get(id=promo_code_id)
                is_valid, _, disc_amt = parse_promo_code(promo_code, subtotal)
                if is_valid:
                    discount = disc_amt
                else:
                    promo_code = None
            except PromoCode.DoesNotExist:
                pass

        final_price = subtotal - discount + delivery_price
        if final_price < decimal.Decimal('0.00'):
            final_price = decimal.Decimal('0.00')

        with transaction.atomic():
            order = Order.objects.create(
                client=request.user.customer_profile,
                delivery_type=delivery_type,
                delivery_address=delivery_address,
                delivery_price=delivery_price,
                pickup_point=pickup_point,
                payment_type=payment_type,
                status=Order.OrderStatus.PENDING,
                promo_code=promo_code,
                final_price=final_price
            )

            for item in items:
                if item.product:
                    product = item.product
                    if product.quantity >= item.quantity:
                        product.quantity -= item.quantity
                    else:
                        product.quantity = 0
                    product.save()

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        purchase_price=product.price,
                        historical_product_name=product.name
                    )

            # Clear cart items and promo code/delivery session
            items.delete()
            request.session.pop('promo_code_id', None)
            request.session.pop('delivery_type', None)
            request.session.pop('pickup_point_id', None)
            request.session.pop('delivery_address', None)
            request.session.pop('payment_type', None)

        return redirect('profile')

    return redirect('purchasing:checkout')

@role_required([User.Role.CUSTOMER])
def order_history_view(request):
    profile = getattr(request.user, 'customer_profile', None)
    history_orders = []
    if profile:
        history_orders = profile.orders.filter(status__in=[Order.OrderStatus.COMPLETED, Order.OrderStatus.CANCELLED]).order_by('-created_at')
    return render(request, 'purchasing/order_history.html', {'history_orders': history_orders})

@role_required([User.Role.CUSTOMER])
def order_details_view(request, order_id):
    profile = getattr(request.user, 'customer_profile', None)
    order = get_object_or_404(Order, id=order_id, client=profile)
    items = order.items.all()

    # Check which products have already been reviewed by this user
    from cms.models import Review
    reviewed_product_ids = set(
        Review.objects.filter(author=request.user, product__in=[item.product for item in items if item.product])
        .values_list('product_id', flat=True)
    )

    # Attach a flag to each item
    for item in items:
        item.already_reviewed = item.product_id in reviewed_product_ids if item.product else False

    return render(request, 'purchasing/order_details.html', {'order': order, 'items': items})

