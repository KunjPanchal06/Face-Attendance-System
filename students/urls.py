from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Page to render the list of students
    path('', views.student_list_view, name='student_list'),

    # Page to render the registration form
    path('add/', views.student_create_view, name='student_create'),
    
    # API to handle data submission
    path('api/register/', views.register_student_api, name='register_student_api'),

    # Delete student
    path('delete/<int:pk>/', views.student_delete_view, name='student_delete'),
]
