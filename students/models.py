from django.db import models
from classrooms.models import Classroom

class Student(models.Model):
    full_name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=50, unique=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    # Store multiple embeddings OR averaged embedding
    face_embeddings = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.roll_no} - {self.full_name}"
