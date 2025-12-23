from django.db import models
from django.contrib.auth.models import User
from classrooms.models import Classroom
from .face_utils import generate_embedding

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=50, unique=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    face_image = models.ImageField(upload_to='students/')
    face_embedding = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)

        # Second phase: generate embedding
        if self.face_image and self.face_embedding is None:
            try:
                self.face_embedding = generate_embedding(self.face_image.path)
                super().save(update_fields=["face_embedding"])
            except Exception as e:
                print("Face embedding error:", e)


        super().save(*args, **kwargs)

    def __str__(self):
        return self.roll_no
