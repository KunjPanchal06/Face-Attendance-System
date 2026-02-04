from django.db import models
from students.models import Student
from classrooms.models import Classroom
from django.utils import timezone

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)  # Date-only field for unique constraint
    present = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'classroom', 'date')  # One attendance per student per classroom per day

    def save(self, *args, **kwargs):
        # Auto-populate date from timestamp
        if self.timestamp:
            self.date = self.timestamp.date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.roll_no} - {self.timestamp}"