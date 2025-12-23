from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserRole
from classrooms.models import Classroom
# from attendance.models import AttendanceSession, AttendanceRecord
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, student_required
from django.contrib.auth.models import User

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
                return redirect('users:admin_dashboard')

            if user_role.role == 'admin':
                return redirect('users:admin_dashboard')
            else:
                return redirect('users:student_dashboard')

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('/users/login')

# @login_required(login_url='/users/login')
# def dashboard_view(request):
#     total_classrooms = Classroom.objects.count()
#     total_students = StudentProfile.objects.count()
#     total_sessions_today = 0
#     total_attendance = 0

#     context = {
#         'total_classrooms': total_classrooms,
#         'total_students': total_students,
#         'total_sessions_today': total_sessions_today,
#         'total_attendance': total_attendance,
#     }

#     return render(request, 'dashboard/dashboard.html', context)

@login_required(login_url='/users/login')
@admin_required
def admin_dashboard_view(request):
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
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required(login_url='/users/login')
@student_required
def student_dashboard_view(request):
    profile = StudentProfile.objects.filter(user=request.user).first()

    attendance_percent = 85
    classes_attended = 40
    classes_missed = 8
    last_session_status = "Present"

    context = {
        'profile': profile,
        'attendance_percent': attendance_percent,
        'classes_attended': classes_attended,
        'classes_missed': classes_missed,
        'last_session_status': last_session_status,
    }
    return render(request, 'dashboard/student_dashboard.html', context)