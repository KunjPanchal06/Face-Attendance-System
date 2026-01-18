from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserRole

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')

        user_role = UserRole.objects.filter(user=request.user).first()

        if not user_role:
            messages.error(request, "Role not assigned. Contact admin.")
            return redirect('users:student_dashboard')

        if user_role.role != 'admin':
            messages.error(request, "Admin access only.")
            return redirect('users:student_dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped

def student_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')

        user_role = UserRole.objects.filter(user=request.user).first()

        if not user_role:
            messages.error(request, "Role not assigned. Contact admin.")
            return redirect('users:login')

        if user_role.role != 'student':
            messages.error(request, "Student access only.")
            return redirect('users:admin_dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped
