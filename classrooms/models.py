from django.db import models

# Create your models here.

class Classroom(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
