from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserRole

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        # if request.user.is_superuser:
        #     return view_func(request, *args, **kwargs)
        
        user_role = UserRole.objects.filter(user=request.user).first()
        if not user_role or user_role.role != 'admin':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('users:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped

def student_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')

        user_role = UserRole.objects.filter(user=request.user).first()
        if not user_role or user_role.role != 'student':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('users:login')

        return view_func(request, *args, **kwargs)
    return _wrapped