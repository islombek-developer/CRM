from django.contrib import admin
from django.urls import path,include
from .views import TeacherPanelView
app_name = 'teachers'

urlpatterns = [
    path('dashboard/',TeacherPanelView.as_view(),name='teacher_dashboard'),
]



