from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def role_required(allowed_roles):
    allowed_roles_str = [str(role) for role in allowed_roles]
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if str(request.user.role) in allowed_roles_str:
                return view_func(request, *args, **kwargs)
            if request.user.is_superuser and ('ADMIN' in allowed_roles_str):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator

def unauthenticated_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
