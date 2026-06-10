from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Role


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            if user_role not in roles:
                messages.error(
                    request,
                    'У вас нет доступа к этой странице. Войдите под учётной записью '
                    'с соответствующей ролью.',
                )
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    return role_required(Role.ADMIN)(view_func)


def manager_or_admin_required(view_func):
    return role_required(Role.MANAGER, Role.ADMIN)(view_func)
