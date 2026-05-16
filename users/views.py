from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from .forms import LoginForm, RegistrationForm
from .models import User, CustomerProfile, StaffProfile
from purchasing.models import Order, OrderItem
from .decorators import role_required, unauthenticated_only

@unauthenticated_only
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user_cache
            login(request, user)
            return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
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
            return redirect('profile')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    if user.role == User.Role.CUSTOMER:
        profile = getattr(user, 'customer_profile', None)
        active_orders = []
        if profile:
            active_orders = profile.orders.exclude(status__in=[Order.OrderStatus.COMPLETED, Order.OrderStatus.CANCELLED]).order_by('-created_at')
        return render(request, 'users/profile_client.html', {
            'profile': profile,
            'active_orders': active_orders
        })
    elif user.role in [User.Role.STAFF, User.Role.ADMIN]:
        profile = getattr(user, 'staff_profile', None)
        return render(request, 'users/profile_staff.html', {
            'profile': profile,
            'user_role': user.get_role_display()
        })
    else:
        return render(request, 'users/profile_client.html', {'profile': None})

@login_required
@role_required([User.Role.CUSTOMER])
def order_history_view(request):
    profile = getattr(request.user, 'customer_profile', None)
    history_orders = []
    if profile:
        history_orders = profile.orders.filter(status__in=[Order.OrderStatus.COMPLETED, Order.OrderStatus.CANCELLED]).order_by('-created_at')
    return render(request, 'users/order_history.html', {'history_orders': history_orders})

@login_required
@role_required([User.Role.CUSTOMER])
def order_details_view(request, order_id):
    profile = getattr(request.user, 'customer_profile', None)
    order = get_object_or_404(Order, id=order_id, client=profile)
    items = order.items.all()
    return render(request, 'users/order_details.html', {'order': order, 'items': items})

@login_required
@role_required([User.Role.ADMIN])
def staff_list_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        staff_user = get_object_or_404(User, id=user_id, role__in=[User.Role.STAFF, User.Role.ADMIN])

        # Don't let an admin revoke their own access via this route accidentally
        if staff_user == request.user:
            messages.error(request, "You cannot revoke your own access.")
        else:
            staff_user.is_active = False
            staff_user.save()
            messages.success(request, f"Access revoked for {staff_user.username}.")
        return redirect('staff_list')

    staff_members = User.objects.filter(role__in=[User.Role.STAFF, User.Role.ADMIN]).order_by('date_joined')
    return render(request, 'users/staff_list.html', {'staff_members': staff_members})
