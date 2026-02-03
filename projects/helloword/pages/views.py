import os
import threading

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotAllowed

from .models import Candidat, Offre, Profile, Postulation, Entretien
from .forms import EntretienForm
from .utils import extract_cv_text, normalize_text, calculer_match_cv_offre


# NOTE SUR L'AVERTISSEMENT "meeting.meeting":
# Si vous voyez l'erreur "RuntimeWarning: Model 'meeting.meeting' was already registered",
# cela signifie probablement que l'application 'meeting' est listée deux fois dans votre
# fichier settings.py sous INSTALLED_APPS. Vérifiez et supprimez le doublon.


# -----------------------------
# Helpers permissions
# -----------------------------
def is_recruteur(user):
    return hasattr(user, "profile") and user.profile.role == "recruteur"


def is_candidat(user):
    return hasattr(user, "profile") and user.profile.role == "candidat"


# -----------------------------
# Email async
# -----------------------------
class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        super().__init__()

    def run(self):
        try:
            send_mail(
                self.subject,
                strip_tags(self.message),
                settings.DEFAULT_FROM_EMAIL,
                self.recipient_list,
                html_message=self.message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")


def envoyer_email_confirmation(candidat_email, candidat_nom, offre_titre, score=None):
    subject = "Confirmation de votre candidature - Khademny"
    html_message = render_to_string(
        "email/confirmation_candidature.html",
        {
            "candidat_nom": candidat_nom,
            "offre_titre": offre_titre,
            "score": score,
            "date": timezone.now().strftime("%d/%m/%Y"),
        },
    )
    EmailThread(subject, html_message, [candidat_email]).start()


# -----------------------------
# Pages principales
# -----------------------------
def home_page_view(request):
    offres = Offre.objects.order_by("-date_publication")
    return render(request, "pages/home.html", {"offres": offres})


def index_view(request):
    return render(request, "pages/index.html")


# -----------------------------
# Auth
# -----------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if is_recruteur(user):
                return redirect("recruteur_page")
            return redirect("home")

        messages.error(request, "Identifiants invalides")

    return render(request, "pages/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Déconnecté avec succès !")
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role")

        if not all([username, email, password1, password2, role]):
            messages.error(request, "Tous les champs sont obligatoires")
        elif password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Nom d'utilisateur déjà pris")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            profile, _ = Profile.objects.get_or_create(user=user, defaults={"role": role})
            if profile.role != role:
                profile.role = role
                profile.save()

            messages.success(request, "Compte créé avec succès !")
            return redirect("login")

    return render(request, "pages/register.html")


# -----------------------------
# Recruteur pages
# -----------------------------
@login_required
def recruteur_page(request):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")
    return render(request, "pages/recruteur.html")


@login_required
def count_view(request):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    offres = Offre.objects.filter(recruteur=request.user).order_by("-date_publication")
    return render(request, "pages/count.html", {"offres": offres})


@login_required
def ajout_offre(request):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    if request.method == "POST":
        titre = request.POST.get("titre")
        description = request.POST.get("description")
        date_expiration = request.POST.get("date_expiration")
        lieu = request.POST.get("lieu")
        salaire = request.POST.get("salaire")
        competences = request.POST.get("competences") or "Python, Django, SQL, Git, Docker, React, JavaScript"

        Offre.objects.create(
            recruteur=request.user,
            titre=titre,
            description=description,
            competences=competences,
            date_expiration=date_expiration,
            lieu=lieu,
            salaire=salaire,
        )

        messages.success(request, "Offre publiée avec succès !")
        return redirect("count")

    return render(request, "pages/ajout_offre.html")


@login_required
def modifier_offre(request, offre_id):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    offre = get_object_or_404(Offre, id=offre_id, recruteur=request.user)

    if request.method == "POST":
        offre.titre = request.POST.get("titre")
        offre.description = request.POST.get("description")
        offre.date_expiration = request.POST.get("date_expiration")
        offre.lieu = request.POST.get("lieu")
        offre.salaire = request.POST.get("salaire")
        offre.competences = request.POST.get("competences", offre.competences)
        offre.save()

        messages.success(request, "Offre modifiée avec succès !")
        return redirect("count")

    return render(request, "pages/modifier_offre.html", {"offre": offre})


@login_required
def supprimer_offre(request, offre_id):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    offre = get_object_or_404(Offre, id=offre_id, recruteur=request.user)
    offre.delete()
    messages.success(request, "Offre supprimée avec succès !")
    return redirect("count")


# -----------------------------
# Liste candidats (recruteur)
# -----------------------------
@login_required
def liste_candidats(request):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    candidats = (
        Candidat.objects.filter(postulations__offre__recruteur=request.user)
        .distinct()
        .order_by("nom", "prenom")
    )
    return render(request, "pages/liste_candidats.html", {"candidats": candidats})


@login_required
def supprimer_candidat(request, candidat_id):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    candidat = get_object_or_404(Candidat, id=candidat_id)
    candidat.delete()
    messages.success(request, "Candidat supprimé avec succès !")
    return redirect("liste_candidats")


# -----------------------------
# ✅ CORRECTION CRUCIALE : Candidat: upload CV + score + postulation
# -----------------------------
@login_required
def candidat_view(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id)

    if request.method == "GET":
        return render(request, "pages/upload_cv.html", {"offre": offre})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    if not request.FILES.get("cv"):
        messages.error(request, "Veuillez sélectionner un fichier CV.")
        return render(request, "pages/upload_cv.html", {"offre": offre, "score": None, "found_skills": []})

    score = None
    found_skills = []

    nom = (request.POST.get("nom") or "").strip()
    prenom = (request.POST.get("prenom") or "").strip()
    email = (request.POST.get("email") or "").strip()
    telephone = (request.POST.get("telephone") or "").strip()
    cv_file = request.FILES["cv"]

    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, cv_file.name)

    with open(temp_path, "wb") as f:
        for chunk in cv_file.chunks():
            f.write(chunk)

    try:
        cv_text = extract_cv_text(temp_path)
        cv_text_norm = normalize_text(cv_text)

        offer_skills = [s.strip().lower() for s in (offre.competences or "").split(",") if s.strip()]
        found_skills = [skill for skill in offer_skills if skill in cv_text_norm]

        score, _ = calculer_match_cv_offre(cv_text_norm, offer_skills)

        # --- DÉBUT DE LA CORRECTION ---
        # Cette section garantit qu'il n'y a qu'UN SEUL objet Candidat par utilisateur.
        try:
            # On essaie de récupérer le candidat existant
            candidat = Candidat.objects.get(user=request.user)
        except Candidat.DoesNotExist:
            # S'il n'existe pas, on en crée un nouveau
            candidat = Candidat.objects.create(
                user=request.user,
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone
            )
        
        # On met à jour les informations du candidat (qu'il soit nouveau ou existant)
        if nom: candidat.nom = nom
        if prenom: candidat.prenom = prenom
        if email: candidat.email = email
        if telephone: candidat.telephone = telephone
        
        candidat.cv = cv_file
        candidat.save()
        # --- FIN DE LA CORRECTION ---

        # On crée ou met à jour la postulation pour éviter les doublons
        postulation, created_p = Postulation.objects.get_or_create(
            candidat=candidat,
            offre=offre,
            defaults={"score": score, "found_skills_text": ", ".join(found_skills)},
        )
        if not created_p:
            postulation.score = score
            postulation.found_skills_text = ", ".join(found_skills)
            postulation.save()

        messages.success(request, "CV analysé ✅ Résultat affiché à gauche.")

        return render(
            request,
            "pages/upload_cv.html",
            {"offre": offre, "score": score, "found_skills": found_skills},
        )

    except Exception as e:
        messages.error(request, f"Erreur lors de l'analyse du CV: {str(e)}")
        return render(
            request,
            "pages/upload_cv.html",
            {"offre": offre, "score": None, "found_skills": []},
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# -----------------------------
# Offres + candidats (recruteur)
# -----------------------------
@login_required
def offres_candidats_view(request):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    offres = (
        Offre.objects.filter(recruteur=request.user)
        .prefetch_related("postulations__candidat", "postulations__entretien")
        .order_by("-date_publication")
    )

    total_postulations = Postulation.objects.filter(offre__recruteur=request.user).count()
    total_candidats = (
        Postulation.objects.filter(offre__recruteur=request.user)
        .values("candidat")
        .distinct()
        .count()
    )
    total_candidatures_qualifiees = Postulation.objects.filter(
        offre__recruteur=request.user, status=Postulation.Status.QUALIFIEE
    ).count()

    return render(
        request,
        "pages/offres_candidats.html",
        {
            "offres": offres,
            "total_candidats": total_candidats,
            "total_postulations": total_postulations,
            "total_candidatures_qualifiees": total_candidatures_qualifiees,
        },
    )


@login_required
def supprimer_candidat_offre(request, candidat_id, offre_id):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    offre = get_object_or_404(Offre, id=offre_id, recruteur=request.user)
    candidat = get_object_or_404(Candidat, id=candidat_id)

    postulation = Postulation.objects.filter(candidat=candidat, offre=offre).first()
    if postulation:
        postulation.delete()
        messages.success(request, "Candidat supprimé de cette offre avec succès !")
    else:
        messages.error(request, "Cette candidature n'existe pas.")

    return redirect("offres_candidats")


# -----------------------------
# Profil
# -----------------------------
@login_required
def mon_profil(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)

        new_password = request.POST.get("new_password")
        if new_password:
            user.set_password(new_password)

        user.save()
        messages.success(request, "Profil mis à jour avec succès !")
        return redirect("mon_profil")

    if profile.role == "recruteur":
        offres_count = Offre.objects.filter(recruteur=request.user).count()
        postulations_count = Postulation.objects.filter(offre__recruteur=request.user).count()
        stats = {"offres_count": offres_count, "postulations_count": postulations_count}
    else:
        # Utilise la relation OneToOne pour récupérer le candidat de manière sûre
        try:
            candidat = request.user.candidat
            postulations_count = Postulation.objects.filter(candidat=candidat).count()
        except Candidat.DoesNotExist:
            postulations_count = 0
        
        stats = {"postulations_count": postulations_count}

    return render(request, "pages/mon_profil.html", {"profile": profile, "stats": stats})


# -----------------------------
# Entretien: planifier
# -----------------------------
@login_required
def planifier_entretien(request, postulation_id):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    postulation = get_object_or_404(Postulation, id=postulation_id, offre__recruteur=request.user)

    if postulation.status != Postulation.Status.QUALIFIEE:
        messages.error(request, "Vous pouvez planifier un entretien فقط للمرشحين qualifiés.")
        return redirect("offres_candidats")

    entretien = getattr(postulation, "entretien", None)

    if request.method == "POST":
        form = EntretienForm(request.POST, instance=entretien)
        if form.is_valid():
            ent = form.save(commit=False)
            ent.postulation = postulation
            ent.save()
            messages.success(request, "Entretien planifié avec succès ✅")
            return redirect("offres_candidats")
    else:
        form = EntretienForm(instance=entretien)

    return render(request, "pages/planifier_entretien.html", {"postulation": postulation, "form": form})


@login_required
def liste_entretiens(request):
    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    entretiens = (
        Entretien.objects.filter(postulation__offre__recruteur=request.user)
        .select_related("postulation__candidat", "postulation__offre")
        .order_by("-scheduled_at")
    )
    return render(request, "pages/liste_entretiens.html", {"entretiens": entretiens})


# -----------------------------
# Statut candidature
# -----------------------------
@login_required
def changer_statut_candidature(request, postulation_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not is_recruteur(request.user):
        return HttpResponseForbidden("Accès refusé")

    postulation = get_object_or_404(Postulation, id=postulation_id, offre__recruteur=request.user)

    new_status = request.POST.get("status")
    allowed = {s[0] for s in Postulation.Status.choices}

    if new_status not in allowed:
        messages.error(request, "Statut invalide.")
        return redirect("offres_candidats")

    postulation.status = new_status
    postulation.save(update_fields=["status"])

    messages.success(request, "Statut mis à jour ✅")
    return redirect("offres_candidats")


# -----------------------------
# Stubs
# -----------------------------
@login_required
def noter_candidat(request, postulation_id):
    messages.info(request, "Fonctionnalité en cours de développement")
    return redirect("offres_candidats")


def recherche_offres(request):
    messages.info(request, "Fonctionnalité en cours de développement")
    return render(request, "pages/recherche_offres.html")


def recherche_candidats(request):
    messages.info(request, "Fonctionnalité en cours de développement")
    return render(request, "pages/recherche_candidats.html")


@login_required
def offres_recommandees(request):
    messages.info(request, "Fonctionnalité en cours de développement")
    return render(request, "pages/offres_recommandees.html")


@login_required
def notifications_view(request):
    messages.info(request, "Fonctionnalité en cours de développement")
    return render(request, "pages/notifications.html")


@login_required
def marquer_notification_vue(request, notification_id):
    messages.info(request, "Fonctionnalité en cours de développement")
    return redirect("notifications")


@login_required
def notifications_count(request):
    return JsonResponse({"count": 0})


@login_required
def statistiques_view(request):
    messages.info(request, "Fonctionnalité en cours de développement")
    return render(request, "pages/statistiques.html")


@login_required
def api_statistiques(request):
    return JsonResponse({"message": "API en construction"})


def contact_view(request):
    messages.info(request, "Fonctionnalité en cours de développement")
    return render(request, "pages/contact.html")


def entreprises_view(request):
    return render(request, "entreprises.html")