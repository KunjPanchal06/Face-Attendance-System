from django.urls import path
from .views import mark_attendance_view, test_attendance_page, start_attendance_session, attendance_reports_view

app_name = "attendance"

urlpatterns = [
    path("mark/", mark_attendance_view, name="mark_attendance"),
    path("test/", test_attendance_page),
    path("start-session/", start_attendance_session, name="start_attendance_session"),
    path("reports/", attendance_reports_view, name="attendance_reports"),
]
