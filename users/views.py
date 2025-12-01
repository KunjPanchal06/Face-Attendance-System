from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserRole, StudentProfile
from classrooms.models import Classroom
# from attendance.models import AttendanceSession, AttendanceRecord
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required


# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
    
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # FIX: safe role fetching
            user_role = UserRole.objects.filter(user=user).first()

            if user_role is None:
                # Default role
                return redirect('dashboard')

            if user_role.role == 'admin':
                return redirect('dashboard')
            else:
                return redirect('dashboard')

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('/users/login')

@login_required(login_url='/users/login')
def dashboard_view(request):
    total_classrooms = Classroom.objects.count()
    total_students = StudentProfile.objects.count()
    total_sessions_today = 0
    total_attendance = 0

    context = {
        'total_classrooms': total_classrooms,
        'total_students': total_students,
        'total_sessions_today': total_sessions_today,
        'total_attendance': total_attendance,
    }

    return render(request, 'dashboard.html', context)