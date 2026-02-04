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
from students.models import Student

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

@login_required(login_url='/users/login')
@admin_required
def admin_dashboard_view(request):
    from django.utils import timezone
    from attendance.models import Attendance
    
    total_classrooms = Classroom.objects.count()
    total_students = Student.objects.count()
    
    # Get today's date range
    today = timezone.localtime(timezone.now()).date()
    
    # Count today's attendance sessions (unique students marked today)
    total_sessions_today = Attendance.objects.filter(date=today).count()
    
    # Total attendance records ever
    total_attendance = Attendance.objects.count()

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
    from django.utils import timezone
    from attendance.models import Attendance
    
    profile = Student.objects.filter(user=request.user).first()
    
    # Default values if no profile found
    attendance_percent = 0
    classes_attended = 0
    classes_missed = 0
    last_session_status = "N/A"
    
    if profile:
        # Get this student's attendance records
        student_attendance = Attendance.objects.filter(student=profile)
        classes_attended = student_attendance.count()
        
        # Get total sessions for this student's classroom
        total_sessions = Attendance.objects.filter(
            classroom=profile.classroom
        ).values('date').distinct().count()
        
        # Calculate missed classes
        classes_missed = max(0, total_sessions - classes_attended)
        
        # Calculate percentage
        if total_sessions > 0:
            attendance_percent = round((classes_attended / total_sessions) * 100, 1)
        
        # Get last session status
        last_record = student_attendance.order_by('-timestamp').first()
        if last_record:
            last_session_status = "Present" if last_record.present else "Absent"

    context = {
        'profile': profile,
        'attendance_percent': attendance_percent,
        'classes_attended': classes_attended,
        'classes_missed': classes_missed,
        'last_session_status': last_session_status,
    }
    return render(request, 'dashboard/student_dashboard.html', context)