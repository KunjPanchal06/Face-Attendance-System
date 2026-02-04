from attendance.models import Attendance
from django.utils import timezone
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

def mark_attendance(student):
    """
    Mark attendance for a student. 
    Returns (attendance_record, created) where created is True if newly marked,
    False if already marked today.
    Only ONE attendance per student per day is allowed.
    """
    now = timezone.localtime(timezone.now())
    today = now.date()
    
    # Check if already marked today
    existing = Attendance.objects.filter(
        student=student,
        classroom=student.classroom,
        date=today
    ).first()
    
    if existing:
        return existing, False
    
    # Create new attendance record
    try:
        attendance = Attendance.objects.create(
            student=student,
            classroom=student.classroom,
            date=today,
            present=True
        )
        return attendance, True
    except IntegrityError:
        # Race condition: another request created the record
        logger.warning(f"IntegrityError for student {student.roll_no} on {today}. Fetching existing record.")
        existing = Attendance.objects.filter(
            student=student,
            classroom=student.classroom,
            date=today
        ).first()
        return existing, False

