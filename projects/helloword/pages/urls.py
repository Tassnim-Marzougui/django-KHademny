# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # Pages principales
    # =========================
    path("", views.home_page_view, name="home"),
    path("home/", views.home_page_view, name="home"),
    path("index/", views.index_view, name="index"),

    # =========================
    # Authentification
    # =========================
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    # =========================
    # Espace recruteur / candidats
    # =========================
    path("recruteur/", views.recruteur_page, name="recruteur_page"),
    path("candidats/", views.liste_candidats, name="liste_candidats"),
    path("candidats/<int:candidat_id>/supprimer/", views.supprimer_candidat, name="supprimer_candidat"),

    # =========================
    # Candidat: postuler (upload CV)
    # =========================
    path("candidat/<int:offre_id>/", views.candidat_view, name="candidat_page"),

    # =========================
    # Offres CRUD
    # =========================
    path("count/", views.count_view, name="count"),
    path("ajout-offre/", views.ajout_offre, name="ajout_offre"),
    path("offre/<int:offre_id>/modifier/", views.modifier_offre, name="modifier_offre"),
    path("offre/<int:offre_id>/supprimer/", views.supprimer_offre, name="supprimer_offre"),

    # =========================
    # Offres + Postulations (recruteur)
    # =========================
    path("offres-candidats/", views.offres_candidats_view, name="offres_candidats"),

    # Supprimer une postulation d'une offre
    path(
        "offres-candidats/<int:offre_id>/candidat/<int:candidat_id>/supprimer/",
        views.supprimer_candidat_offre,
        name="supprimer_candidat_offre",
    ),

    # ✅ Changer statut candidature (POST recommandé)
    path(
        "postulation/<int:postulation_id>/status/",
        views.changer_statut_candidature,
        name="changer_statut_candidature",
    ),

    # ✅ Planifier entretien (GET/POST)
    path(
        "postulation/<int:postulation_id>/entretien/",
        views.planifier_entretien,
        name="planifier_entretien",
    ),

    # ✅ Liste entretiens (recruteur)
    path("entretiens/", views.liste_entretiens, name="liste_entretiens"),

    # =========================
    # Profil
    # =========================
    path("mon-profil/", views.mon_profil, name="mon_profil"),

    # =========================
    # Autres pages (stubs)
    # =========================
    path("noter-candidat/<int:postulation_id>/", views.noter_candidat, name="noter_candidat"),
    path("recherche-offres/", views.recherche_offres, name="recherche_offres"),
    path("recherche-candidats/", views.recherche_candidats, name="recherche_candidats"),
    path("offres-recommandees/", views.offres_recommandees, name="offres_recommandees"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("notifications/marquer-vue/<int:notification_id>/", views.marquer_notification_vue, name="marquer_notification_vue"),
    path("api/notifications/count/", views.notifications_count, name="notifications_count"),
    path("statistiques/", views.statistiques_view, name="statistiques"),
    path("api/statistiques/", views.api_statistiques, name="api_statistiques"),
    path("contact/", views.contact_view, name="contact"),
    path("entreprises/", views.entreprises_view, name="entreprises"),
]
