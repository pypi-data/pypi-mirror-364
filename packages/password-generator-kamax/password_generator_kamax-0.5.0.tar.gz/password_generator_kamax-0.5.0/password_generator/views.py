from django.http import JsonResponse
from .generator import generate_password  # Supposons que tu as cette fonction

def generate_password(request):
    password = generate_password(length=12)
    return JsonResponse({'password': password})