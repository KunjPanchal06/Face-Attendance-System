from django.contrib import admin
from .models import Classroom

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')
    search_fields = ('name',)
