from django.urls import path
from .views import mark_attendance_view, test_attendance_page

urlpatterns = [
    path("mark/", mark_attendance_view, name="mark_attendance"),
    path("test/", test_attendance_page),
]
