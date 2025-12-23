from attendance.models import Attendance
from django.utils import timezone

def mark_attendance(student):
    today = timezone.now().date()

    attendance, created = Attendance.objects.get_or_create(
        student=student,
        date=today,
        classroom=student.classroom,
        defaults={"present": True}
    )

    return attendance, created
