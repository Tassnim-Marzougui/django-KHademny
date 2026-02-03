# app/admin.py
from django.contrib import admin
from .models import Profile, Candidat, Offre, Postulation

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    search_fields = ("user__username", "role")

@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "email", "telephone", "user")
    search_fields = ("nom", "prenom", "email")
    list_filter = ("user",)

@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ("titre", "recruteur", "lieu", "salaire", "date_expiration", "est_active")
    search_fields = ("titre", "description", "lieu")
    list_filter = ("recruteur", "date_expiration")

@admin.register(Postulation)
class PostulationAdmin(admin.ModelAdmin):
    list_display = ("candidat", "offre", "date_postulation", "score")
    search_fields = ("candidat__nom", "candidat__prenom", "offre__titre")
    list_filter = ("offre", "date_postulation")
