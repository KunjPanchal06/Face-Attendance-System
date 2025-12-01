from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserRole

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
    
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            role = UserRole.objects.get(user=user).role

            if role == 'admin':
                return redirect('/admin_dashboard')
            else:
                return redirect('/student_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
        
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('/users/login')