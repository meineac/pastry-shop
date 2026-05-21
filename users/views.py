import logging
from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Category, Product
from purchasing.models import Order
from .decorators import role_required, unauthenticated_only
from .forms import LoginForm, RegistrationForm, StaffCreationForm
from .models import CustomerProfile, StaffProfile, User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@unauthenticated_only
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user_cache
            login(request, user)
            logger.info("User '%s' logged in.", user.username)
            return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logger.info("User '%s' logged out.", request.user.username)
    logout(request)
    return redirect('login')


@unauthenticated_only
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.role = User.Role.CUSTOMER
                user.save()

                CustomerProfile.objects.create(
                    user=user,
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    phone_number=form.cleaned_data['phone_number']
                )
            login(request, user)
            logger.info("New customer '%s' registered.", user.username)
            return redirect('profile')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@login_required
def profile_view(request):
    user = request.user
    if user.role == User.Role.CUSTOMER:
        profile = getattr(user, 'customer_profile', None)
        active_orders = []
        if profile:
            active_orders = profile.orders.exclude(
                status__in=[Order.OrderStatus.COMPLETED, Order.OrderStatus.CANCELLED]
            ).order_by('-created_at')
        return render(request, 'users/profile_client.html', {
            'profile': profile,
            'active_orders': active_orders,
        })
    elif user.role in [User.Role.STAFF, User.Role.ADMIN]:
        profile = getattr(user, 'staff_profile', None)
        return render(request, 'users/profile_staff.html', {
            'profile': profile,
            'user_role': user.get_role_display(),
        })
    else:
        return render(request, 'users/profile_client.html', {'profile': None})


# ---------------------------------------------------------------------------
# Staff list (Admin only)
# ---------------------------------------------------------------------------

@role_required([User.Role.ADMIN])
def staff_list_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        staff_user = get_object_or_404(User, id=user_id, role__in=[User.Role.STAFF, User.Role.ADMIN])

        if staff_user == request.user:
            messages.error(request, "You cannot modify your own access.")
        else:
            if action == 'return':
                staff_user.is_active = True
                staff_user.save()
                logger.info(
                    "Admin '%s' returned access for user '%s'.",
                    request.user.username, staff_user.username
                )
                messages.success(request, f"Access restored for {staff_user.username}.")
            else:
                staff_user.is_active = False
                staff_user.save()
                logger.warning(
                    "Admin '%s' revoked access for user '%s'.",
                    request.user.username, staff_user.username
                )
                messages.success(request, f"Access revoked for {staff_user.username}.")
        return redirect('staff_list')

    staff_members = User.objects.filter(
        role__in=[User.Role.STAFF, User.Role.ADMIN]
    ).order_by('date_joined')
    return render(request, 'users/staff_list.html', {'staff_members': staff_members})


@role_required([User.Role.ADMIN])
def staff_create_view(request):
    """
    Admin-only view for creating a new Staff User and their StaffProfile
    simultaneously via a single unified form.
    Both records are saved inside an atomic transaction so the database
    is never left in a partial state.
    """
    if request.method == 'POST':
        form = StaffCreationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = User(
                    username=form.cleaned_data['username'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    role=User.Role.STAFF,
                )
                user.set_password(form.cleaned_data['password'])
                user.save()

                StaffProfile.objects.create(
                    user=user,
                    position=form.cleaned_data['position'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    contact_details=form.cleaned_data['contact_details'],
                    photo=form.cleaned_data.get('photo'),
                )

            logger.info(
                "Admin '%s' created new staff account '%s'.",
                request.user.username, user.username
            )
            messages.success(
                request,
                f"Staff account '{user.username}' created successfully."
            )
            return redirect('staff_list')
    else:
        form = StaffCreationForm()

    return render(request, 'users/staff_create.html', {'form': form})


# ---------------------------------------------------------------------------
# Helpers for client views
# ---------------------------------------------------------------------------

def _get_staff_profile(user):
    """Return the StaffProfile for admin/staff, or None if not yet created."""
    return getattr(user, 'staff_profile', None)


def _calculate_age(date_of_birth):
    """Calculate age in whole years from a date_of_birth date."""
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def _my_clients_qs(staff_profile):
    """Return the my_clients queryset for a staff profile, or empty qs."""
    if staff_profile is None:
        return CustomerProfile.objects.none()
    return staff_profile.my_clients.all()


# ---------------------------------------------------------------------------
# Clients (Admin & Staff)
# ---------------------------------------------------------------------------

@role_required([User.Role.ADMIN, User.Role.STAFF])
def client_list_view(request):
    """
    Lists all CustomerProfiles with name, received/cancelled order counts.
    Supports search by name and filters by product, category (product tag),
    and last-order date range. Staff/admin can add a client to their list.
    """
    staff_profile = _get_staff_profile(request.user)

    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        client = get_object_or_404(CustomerProfile, id=client_id)
        if staff_profile is None:
            messages.error(request, "You need a Staff Profile to maintain a client list.")
        else:
            staff_profile.my_clients.add(client)
            logger.info(
                "Staff '%s' added client '%s' to their list.",
                request.user.username, client
            )
            messages.success(request, f"{client} added to your client list.")
        return redirect('client_list')

    clients = CustomerProfile.objects.annotate(
        received_orders=Count('orders', filter=Q(orders__status=Order.OrderStatus.COMPLETED)),
        cancelled_orders=Count('orders', filter=Q(orders__status=Order.OrderStatus.CANCELLED)),
    ).select_related('user').order_by('user__first_name', 'user__last_name', 'user__username')

    # Search by name / username
    q = request.GET.get('q', '').strip()
    if q:
        clients = clients.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__username__icontains=q)
        )

    # Filter by purchased product (completed orders only)
    product_id = request.GET.get('product', '').strip()
    if product_id:
        clients = clients.filter(
            orders__items__product_id=product_id,
            orders__status=Order.OrderStatus.COMPLETED,
        ).distinct()

    # Filter by product category (product tag)
    category_id = request.GET.get('category', '').strip()
    if category_id:
        clients = clients.filter(
            orders__items__product__category_id=category_id,
            orders__status=Order.OrderStatus.COMPLETED,
        ).distinct()

    # Filter by last order date range
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    if date_from:
        clients = clients.filter(orders__created_at__date__gte=date_from)
    if date_to:
        clients = clients.filter(orders__created_at__date__lte=date_to)
    if date_from or date_to:
        clients = clients.distinct()

    my_client_ids = set(_my_clients_qs(staff_profile).values_list('id', flat=True))

    context = {
        'clients': clients,
        'my_client_ids': my_client_ids,
        'products': Product.objects.filter(is_active=True).order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'q': q,
        'product_id': product_id,
        'category_id': category_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'users/client_list.html', context)


@role_required([User.Role.ADMIN, User.Role.STAFF])
def client_card_view(request, client_id):
    """
    Detail view for a single CustomerProfile: name, age, registration date,
    contact info, list of orders and reviews.
    """
    client = get_object_or_404(CustomerProfile, id=client_id)
    age = _calculate_age(client.date_of_birth)
    orders = client.orders.order_by('-created_at')
    reviews = client.user.reviews.select_related('product').order_by('-created_at')

    context = {
        'client': client,
        'age': age,
        'orders': orders,
        'reviews': reviews,
    }
    return render(request, 'users/client_card.html', context)


@role_required([User.Role.ADMIN, User.Role.STAFF])
def my_clients_view(request):
    """
    Lists only the clients the current staff/admin is working with.
    Supports the same search and filters as client_list_view.
    Has a Remove button instead of Add.
    """
    staff_profile = _get_staff_profile(request.user)

    clients = _my_clients_qs(staff_profile).annotate(
        received_orders=Count('orders', filter=Q(orders__status=Order.OrderStatus.COMPLETED)),
        cancelled_orders=Count('orders', filter=Q(orders__status=Order.OrderStatus.CANCELLED)),
    ).select_related('user').order_by('user__first_name', 'user__last_name', 'user__username')

    q = request.GET.get('q', '').strip()
    if q:
        clients = clients.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__username__icontains=q)
        )

    product_id = request.GET.get('product', '').strip()
    if product_id:
        clients = clients.filter(
            orders__items__product_id=product_id,
            orders__status=Order.OrderStatus.COMPLETED,
        ).distinct()

    category_id = request.GET.get('category', '').strip()
    if category_id:
        clients = clients.filter(
            orders__items__product__category_id=category_id,
            orders__status=Order.OrderStatus.COMPLETED,
        ).distinct()

    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    if date_from:
        clients = clients.filter(orders__created_at__date__gte=date_from)
    if date_to:
        clients = clients.filter(orders__created_at__date__lte=date_to)
    if date_from or date_to:
        clients = clients.distinct()

    context = {
        'clients': clients,
        'products': Product.objects.filter(is_active=True).order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'q': q,
        'product_id': product_id,
        'category_id': category_id,
        'date_from': date_from,
        'date_to': date_to,
        'staff_has_profile': staff_profile is not None,
    }
    return render(request, 'users/my_clients.html', context)


@role_required([User.Role.ADMIN, User.Role.STAFF])
def client_remove_view(request, client_id):
    """POST-only: removes a client from the staff member's personal client list."""
    if request.method != 'POST':
        raise PermissionDenied

    staff_profile = _get_staff_profile(request.user)
    if staff_profile is None:
        messages.error(request, "You need a Staff Profile to manage a client list.")
        return redirect('my_clients')

    client = get_object_or_404(CustomerProfile, id=client_id)
    staff_profile.my_clients.remove(client)
    logger.info(
        "Staff '%s' removed client '%s' from their list.",
        request.user.username, client
    )
    messages.success(request, f"{client} removed from your client list.")
    return redirect('my_clients')
