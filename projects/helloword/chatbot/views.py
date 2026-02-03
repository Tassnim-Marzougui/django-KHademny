from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .utils import handle_message

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_view(request):
    try:
        # Essayer de récupérer les données depuis request.POST d'abord
        if request.POST.get("message"):
            msg = request.POST.get("message", "").strip()
        else:
            # Sinon essayer depuis le body JSON
            data = json.loads(request.body)
            msg = data.get("message", "").strip()

        if not msg:
            return JsonResponse({"reply": "⚠️ Aucun message reçu."}, status=400)

        # Utiliser votre fonction handle_message existante
        reply = handle_message(msg)

        return JsonResponse({"reply": reply}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"reply": "❌ Format de requête invalide."}, status=400)
    except Exception as e:
        return JsonResponse({"reply": f"❌ Erreur serveur: {str(e)}"}, status=500)