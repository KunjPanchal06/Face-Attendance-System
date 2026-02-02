from django.http import JsonResponse, HttpResponse
from students.face_utils import generate_embedding
from attendance.face_matcher import find_matching_student
from attendance.services import mark_attendance
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.decorators import admin_required
from .models import Attendance
from students.models import Student
from classrooms.models import Classroom
from django.utils import timezone
from datetime import datetime, timedelta
import csv
# from attendance.camera_attendance import start_camera_attendance

def mark_attendance_view(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        embedding = generate_embedding(image)

        student, similarity = find_matching_student(embedding)

        if student:
            print(f"MATCH FOUND: Student {student.roll_no} with similarity {similarity}")
            attendance, created = mark_attendance(student)
            print(f"Attendance marked: {created}")
            return JsonResponse({
                "status": "success",
                "student": f"{student.full_name} ({student.roll_no})",
                "similarity": similarity,
                "marked": created
            })

        print(f"NO MATCH FOUND. Max similarity was likely below threshold.")
        return JsonResponse({"status": "no_match"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

def test_attendance_page(request):
    result = None

    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        embedding = generate_embedding(image)
        student, similarity = find_matching_student(embedding)

        if student:
            attendance, created = mark_attendance(student)
            result = f"Matched {student.roll_no}, similarity={similarity:.2f}"
        else:
            result = "No match found"

    return render(request, "attendance_test.html", {"result": result})

def start_attendance_session(request):
    """
    Renders the frontend page for live attendance.
    The actual processing happens via AJAX calls to mark_attendance_view.
    """
    return render(request, "attendance/attendance_session.html")


@login_required(login_url='/users/login')
@admin_required
def attendance_reports_view(request):
    """
    Display attendance reports with filtering options.
    Supports filtering by date range, classroom, and student.
    Also supports CSV export.
    """
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    classroom_id = request.GET.get('classroom')
    student_id = request.GET.get('student')
    export_csv = request.GET.get('export') == 'csv'
    
    # Base queryset
    attendance_records = Attendance.objects.select_related('student', 'classroom').order_by('-timestamp')
    
    # Apply filters
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_dt = timezone.make_aware(start_dt) if timezone.is_naive(start_dt) else start_dt
            attendance_records = attendance_records.filter(timestamp__gte=start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_dt = end_dt + timedelta(days=1)  # Include the entire end date
            end_dt = timezone.make_aware(end_dt) if timezone.is_naive(end_dt) else end_dt
            attendance_records = attendance_records.filter(timestamp__lt=end_dt)
        except ValueError:
            pass
    
    if classroom_id:
        attendance_records = attendance_records.filter(classroom_id=classroom_id)
    
    if student_id:
        attendance_records = attendance_records.filter(student_id=student_id)
    
    # CSV Export
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Student Name', 'Classroom', 'Date', 'Time', 'Status'])
        
        for record in attendance_records:
            writer.writerow([
                record.student.roll_no,
                record.student.full_name,
                record.classroom.name,
                record.timestamp.strftime('%Y-%m-%d'),
                record.timestamp.strftime('%H:%M:%S'),
                'Present' if record.present else 'Absent'
            ])
        
        return response
    
    # Calculate stats
    total_records = attendance_records.count()
    present_count = attendance_records.filter(present=True).count()
    absent_count = attendance_records.filter(present=False).count()
    
    # Today's attendance
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_attendance = Attendance.objects.filter(timestamp__gte=today_start).count()
    
    # Get all classrooms and students for filter dropdowns
    classrooms = Classroom.objects.all().order_by('name')
    students = Student.objects.all().order_by('roll_no')
    
    # Pagination (simple limit for now)
    attendance_list = attendance_records[:100]
    
    context = {
        'attendance_records': attendance_list,
        'classrooms': classrooms,
        'students': students,
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'today_attendance': today_attendance,
        # Preserve filter values
        'selected_start_date': start_date or '',
        'selected_end_date': end_date or '',
        'selected_classroom': classroom_id or '',
        'selected_student': student_id or '',
    }
    
    return render(request, "attendance/attendance_reports.html", context)