# password_generator/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_password, name='generate_password'),
]
