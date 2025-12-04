from django.urls import path
from .views import login_view, logout_view, admin_dashboard_view, student_dashboard_view

app_name = 'users'

urlpatterns = [
    path('login/', login_view, name = 'login'),
    path('logout/', logout_view, name = 'logout'),

    path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('student/dashboard/', student_dashboard_view, name='student_dashboard'),
]
