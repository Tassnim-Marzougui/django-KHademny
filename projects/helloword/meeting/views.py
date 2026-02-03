from django.shortcuts import render
from pages.models import Candidat
from .models import Meeting
from django.contrib import messages
from pages.models import Offre  # si tu veux utiliser les offres
from helloword.compatibilite import evaluer_compatibilite

# -----------------------------
# Pages
# -----------------------------
def count_view(request):
    offres = Offre.objects.all()
    return render(request, "pages/home.html", {"offres": offres})

# -----------------------------
# Exemple vue pour compatibilité CV
# -----------------------------
def candidat_view(request, offer_id=None):
    score_percent = 0.0
    found_skills = []
    offre = None

    if offer_id:
        try:
            offre = Offre.objects.get(id=offer_id)
            offer_skills = [s.strip() for s in offre.competences.split(",")] if offre.competences else []
        except Offre.DoesNotExist:
            messages.warning(request, "Offre introuvable")
            return redirect("home_page")
    else:
        offer_skills = []

    if request.method == "POST" and request.FILES.get("cv"):
        cv_file = request.FILES["cv"]
        temp_path = f"media/{cv_file.name}"

        with open(temp_path, "wb") as f:
            for chunk in cv_file.chunks():
                f.write(chunk)

        try:
            # 👉 Utilisation de la fonction compatibilité
            score, niveau, competences_trouvees = evaluer_compatibilite(temp_path, offer_skills)
            score_percent = round(score, 2)
            found_skills = competences_trouvees

            if score_percent >= 70:
                messages.success(request, f"✅ Score compatibilité : {score_percent}% → Acceptable")
            else:
                messages.warning(request, f"⚠️ Score compatibilité : {score_percent}% → Faible")

        except Exception as e:
            messages.error(request, f"⚠️ Impossible de traiter le CV : {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        try:
            Candidat.objects.create(
                user=request.user,
                nom=request.POST.get("nom"),
                prenom=request.POST.get("prenom"),
                email=request.POST.get("email"),
                telephone=request.POST.get("telephone", ""),
                cv=cv_file,
            )
            messages.info(request, "✅ Candidat enregistré avec succès !")
        except Exception as e:
            messages.error(request, f"⚠️ Impossible d'enregistrer le candidat : {e}")

    return render(request, "pages/candidat.html", {
        "found_skills": found_skills,
        "score_result": score_percent,
        "offer": offre,
    })

def login_view(request):
    return render(request, 'login.html')


def liste_candidats(request):
    candidats = Candidat.objects.all()
    return render(request, "pages/liste_candidats.html", {"candidats": candidats})
