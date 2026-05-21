from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.core.exceptions import PermissionDenied

from users.decorators import role_required
from users.models import User
from .models import Order
from .services import update_order_status


@role_required([User.Role.ADMIN, User.Role.STAFF])
def active_orders_view(request):
    """
    Dashboard for staff to manage active orders.
    Sort priority:
    1. READY
    2. PROCESSING
    3. PENDING
    Secondary sort: created_at ascending (oldest first).
    """
    active_statuses = [
        Order.OrderStatus.PENDING,
        Order.OrderStatus.PROCESSING,
        Order.OrderStatus.READY,
    ]

    orders = Order.objects.filter(status__in=active_statuses).annotate(
        status_priority=Case(
            When(status=Order.OrderStatus.READY, then=1),
            When(status=Order.OrderStatus.PROCESSING, then=2),
            When(status=Order.OrderStatus.PENDING, then=3),
            default=4,
            output_field=IntegerField(),
        )
    ).order_by('status_priority', 'created_at')

    return render(request, 'purchasing/staff_orders.html', {'orders': orders})


@role_required([User.Role.ADMIN, User.Role.STAFF])
def update_order_status_view(request, order_id):
    """
    POST-only endpoint to update an order's status.
    Accepts 'new_status' in POST data.
    Redirects back to the referrer or a default page.
    """
    if request.method != 'POST':
        raise PermissionDenied

    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('new_status')

    valid_statuses = [choice[0] for choice in Order.OrderStatus.choices]

    if new_status not in valid_statuses:
        messages.error(request, "Invalid status.")
    else:
        success = update_order_status(order, new_status, request.user)
        if success:
            messages.success(request, f"Order #{order.id} status updated to {new_status}.")
        else:
            messages.error(request, f"Could not update status for Order #{order.id}.")

    # Redirect back to where the request came from, default to active orders list
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'purchasing:active_orders'
    return redirect(next_url)
