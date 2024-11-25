from django.contrib import admin
from django.urls import path
from .views import LoginView,RegisterView,GroupPaymentListView,Home,LogautView,GroupCreateView,TeacherView,GroupDeleteView
from .student import StudentCreateView,StudentListView,StudentUpdateView,StudentDeleteView

urlpatterns = [

    path('',LoginView.as_view(),name='login'),
    path('logout/',LogautView.as_view(),name='logout'),
    path('register/',RegisterView.as_view(),name='register'),
    path('group-payment/',GroupPaymentListView.as_view(),name='group_payment'),
    path('dashboard/', Home.as_view(),name='dashboard'),
    path('create/', StudentCreateView.as_view(), name='student_create'),
    path('students/<int:group_id>/', StudentListView.as_view(), name='student_list'),
    path('update/<int:pk>/', StudentUpdateView.as_view(), name='update_student'),
    path('delete/<int:pk>/', StudentDeleteView.as_view(), name='delete_student'),
    path('teacher/', TeacherView.as_view(), name='teacher'),
    path('groups/<int:pk>/delete/', GroupDeleteView.as_view(), name='delete_group'),
    path('groups/create/', GroupCreateView.as_view(), name='create_group'),
]