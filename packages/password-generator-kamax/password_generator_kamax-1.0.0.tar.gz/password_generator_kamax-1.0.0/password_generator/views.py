from django.http import JsonResponse
from .generator import generate_password

def generate_password_view(request):
    try:
        # Récupérer la longueur depuis les paramètres GET, ex: ?length=16
        length = int(request.GET.get("length", 12))
        password = generate_password(length=length)
        return JsonResponse({'password': password})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
