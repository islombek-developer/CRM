from django.contrib import admin
from django.urls import path
from .views import LoginView,RegisterView,GroupPaymentListView,Home,LogautView,GroupCreateView,TeacherView,GroupDeleteView,GroupPaymentsListView
from .student import StudentCreateView,StudentListView,StudentUpdateView,StudentDeleteView
from . import views





urlpatterns = [
    path('add_payment/<int:student_id>/', views.add_payment, name='add_payment'),
    path('student_payment_history/<int:student_id>/', views.student_payment_history, name='student_payment_history'),
    path('group_payment_report/<int:group_id>/', views.group_payment_report, name='group_payment_report'),

    path('',LoginView.as_view(),name='login'),
    path('logout/',LogautView.as_view(),name='logout'),
    path('register/',RegisterView.as_view(),name='register'),
    path('groups/',GroupPaymentListView.as_view(),name='group_payment'),
    path('group-payment/s',GroupPaymentsListView.as_view(),name='group_payments'),
    path('dashboard/', Home.as_view(),name='dashboard'),
    path('students/create/', StudentCreateView.as_view(), name='student_create'),
    path('students/create/<int:group_id>/', StudentCreateView.as_view(), name='student_create_with_group'),
    path('students/<int:group_id>/', StudentListView.as_view(), name='student_list_by_group'),
    path('students/<int:group_id>/', StudentListView.as_view(), name='student_list'),
    path('update/<int:pk>/', StudentUpdateView.as_view(), name='update_student'),
    path('delete/<int:pk>/', StudentDeleteView.as_view(), name='delete_student'),
    path('teacher/', TeacherView.as_view(), name='teacher'),
    path('groups/<int:pk>/delete/', GroupDeleteView.as_view(), name='delete_group'),
    path('groups/create/', GroupCreateView.as_view(), name='create_group'),

       

]