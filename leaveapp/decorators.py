from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Profile


def manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile = request.user.profile
        if profile.role not in {Profile.ROLE_MANAGER, Profile.ROLE_ADMIN}:
            messages.error(request, "此功能僅限主管或管理者使用。")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper


def employee_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role != Profile.ROLE_EMPLOYEE:
            messages.error(request, "此功能僅限一般員工使用。")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper
