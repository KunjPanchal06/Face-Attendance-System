from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_no', 'user', 'classroom')
    search_fields = ('roll_no', 'user__username')