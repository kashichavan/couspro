from django.core.exceptions import PermissionDenied
from functools import wraps

from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('accounts:unauthorized')
        return _wrapped_view
    return decorator

# For convenience
def manager_required(view_func):
    return role_required(['manager'])(view_func)

def counselor_required(view_func):
    return role_required(['counselor'])(view_func)
