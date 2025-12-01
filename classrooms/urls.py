from django.urls import path
from . import views

urlpatterns = [
    path('', views.classroom_list, name='classroom_list'),
    path('create/', views.classroom_create, name='classroom_create'),
    path('<int:id>/edit/', views.classroom_edit, name='classroom_edit'),
    path('<int:id>/delete/', views.classroom_delete, name='classroom_delete'),
]