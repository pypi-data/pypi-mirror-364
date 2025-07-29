from django.urls import path
from .views import generate_password_view

urlpatterns = [
    path('generate/', generate_password_view, name='generate_password'),
]
