from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'roll_no', 'classroom')
    search_fields = ('roll_no', 'user__username')