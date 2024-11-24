from django.contrib import admin
from django.urls import path
from .views import home

urlpatterns = [
    path('dashboard/', home,name='dashboard'),
    # path('',LoginView,name='login'),
    # path('register/',RegisterView,name='register')
]