
from django.http import JsonResponse
from .generator import generate_password

def generate_password_view(request):
    try:
        length = int(request.GET.get("length", 12))  
        password = generate_password(length=length)
        return JsonResponse({"password": password})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)