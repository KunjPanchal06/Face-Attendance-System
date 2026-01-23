from attendance.models import Attendance
from django.utils import timezone

def mark_attendance(student):
    """
    Mark attendance for a student. 
    Returns (attendance_record, created) where created is True if newly marked,
    False if already marked today.
    Only ONE attendance per student per day is allowed.
    """
    # Get current time in LOCAL timezone
    now = timezone.localtime(timezone.now())
    today = now.date()
    
    print(f"[DEBUG] Current local time: {now}, Date: {today}")
    print(f"[DEBUG] Checking attendance for Student {student.roll_no} on {today}")
    
    # Check if already marked today
    # Get start and end of today in local timezone, then convert to UTC for query
    from datetime import datetime, time, timedelta
    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(datetime.combine(today, time.max))
    
    print(f"[DEBUG] Checking between {start_of_day} and {end_of_day}")
    
    existing = Attendance.objects.filter(
        student=student,
        classroom=student.classroom,
        timestamp__gte=start_of_day,
        timestamp__lte=end_of_day
    ).first()
    
    if existing:
        print(f"[DEBUG] Already marked! Record ID: {existing.id}, Time: {existing.timestamp}")
        return existing, False
    
    # Create new attendance record
    print(f"[DEBUG] Creating new attendance record for Student {student.roll_no}")
    attendance = Attendance.objects.create(
        student=student,
        classroom=student.classroom,
        present=True
    )
    
    print(f"[DEBUG] Created record ID: {attendance.id}")
    return attendance, True
