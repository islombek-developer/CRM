from django.contrib import admin
from django.urls import path
from .views import LoginView,RegisterView,GroupPaymentListView,Home,LogautView,CreateGroupView
from .student import CreateStudentView,StudentListView,UpdateStudentView,DeleteStudentView

urlpatterns = [

    path('',LoginView.as_view(),name='login'),
    path('logout/',LogautView.as_view(),name='logout'),
    path('register/',RegisterView.as_view(),name='register'),
    path('group-payment/',GroupPaymentListView.as_view(),name='group_payment'),
    path('dashboard/', Home.as_view(),name='dashboard'),
    path('create/', CreateStudentView.as_view(), name='create-student'),
    path('students/<int:group_id>/', StudentListView.as_view(), name='student_list'),
    path('update/<int:pk>/', UpdateStudentView.as_view(), name='update_student'),
    path('delete/<int:pk>/', DeleteStudentView.as_view(), name='delete_student'),
    path('create/', CreateGroupView.as_view(), name='create_group'),
]