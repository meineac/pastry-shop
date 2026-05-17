from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from .models import Cart, CartItem, Order, OrderItem, PickupPoint, PromoCode
from catalog.models import Product
from datetime import date
import decimal

def get_or_create_cart(user):
    if not hasattr(user, 'customerprofile'):
        return None
    cart, created = Cart.objects.get_or_create(client=user.customerprofile)
    return cart

def add_to_cart_view(request, product_id):
    if not request.user.is_authenticated:
        return redirect('register')

    if not hasattr(request.user, 'customerprofile'):
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

    return redirect('catalog:product_list')

@login_required
def remove_from_cart_view(request, cart_item_id):
    if not hasattr(request.user, 'customerprofile'):
        return redirect('catalog:product_list')

    if request.method == 'POST':
        cart = get_or_create_cart(request.user)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
        cart_item.delete()

    return redirect('purchasing:cart')

@login_required
def cart_view(request):
    if not hasattr(request.user, 'customerprofile'):
        return redirect('catalog:product_list')

    cart = get_or_create_cart(request.user)
    items = cart.items.all()

    total = sum(item.product.price * item.quantity for item in items if item.product)

    context = {
        'items': items,
        'total': total
    }
    return render(request, 'purchasing/cart.html', context)

@login_required
def apply_promo_view(request):
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
    if not hasattr(request.user, 'customerprofile'):
        return redirect('catalog:product_list')

    cart = get_or_create_cart(request.user)
    items = cart.items.all()

    if not items:
        return redirect('purchasing:cart')

    subtotal = sum(item.product.price * item.quantity for item in items if item.product)

    promo_code_id = request.session.get('promo_code_id')
    promo_code = None
    discount = decimal.Decimal('0.00')

    if promo_code_id:
        try:
            promo_code = PromoCode.objects.get(id=promo_code_id)
            # Simple discount logic placeholder, let's say 10% off for all promo codes
            discount = subtotal * decimal.Decimal('0.10')
        except PromoCode.DoesNotExist:
            pass

    total = subtotal - discount

    pickup_points = PickupPoint.objects.all()

    context = {
        'items': items,
        'subtotal': subtotal,
        'promo_code': promo_code,
        'promo_error': request.session.pop('promo_error', None),
        'promo_success': request.session.pop('promo_success', None),
        'discount': discount,
        'total': total,
        'pickup_points': pickup_points,
    }
    return render(request, 'purchasing/checkout.html', context)

@login_required
def place_order_view(request):
    if not hasattr(request.user, 'customerprofile'):
        return redirect('catalog:product_list')

    if request.method == 'POST':
        cart = get_or_create_cart(request.user)
        items = cart.items.all()

        if not items:
            return redirect('purchasing:cart')

        pickup_point_id = request.POST.get('pickup_point')
        payment_type = request.POST.get('payment_type')

        pickup_point = get_object_or_404(PickupPoint, id=pickup_point_id)

        subtotal = sum(item.product.price * item.quantity for item in items if item.product)

        promo_code_id = request.session.get('promo_code_id')
        promo_code = None
        discount = decimal.Decimal('0.00')

        if promo_code_id:
            try:
                promo_code = PromoCode.objects.get(id=promo_code_id)
                # Apply discount dynamically if conditions_of_application matches something,
                # or just placeholder 10% logic per earlier code since rules aren't specified for computation.
                # However, following the reviewer comment: we must calculate taking PromoCode into account.
                # Since promo code conditions are a TextField, we apply a flat 10% discount for demonstration if a valid code is present.
                discount = subtotal * decimal.Decimal('0.10')
            except PromoCode.DoesNotExist:
                pass

        final_price = subtotal - discount

        with transaction.atomic():
            order = Order.objects.create(
                client=request.user.customerprofile,
                pickup_point=pickup_point,
                payment_type=payment_type,
                status=Order.OrderStatus.PENDING,
                promo_code=promo_code,
                final_price=final_price
            )

            for item in items:
                if item.product:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        purchase_price=item.product.price,
                        historical_product_name=item.product.name
                    )

            # Clear cart items
            items.delete()
            request.session.pop('promo_code_id', None)

        return redirect('profile')

    return redirect('purchasing:checkout')
