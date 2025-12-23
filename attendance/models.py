from django.db import models
from students.models import Student
from classrooms.models import Classroom
from django.utils import timezone

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    present = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.roll_no} - {self.date}"