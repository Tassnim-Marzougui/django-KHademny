from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# =========================
# Profile (role)
# =========================
class Profile(models.Model):
    ROLE_CHOICES = [
        ("candidat", "Candidat"),
        ("recruteur", "Recruteur"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# =========================
# Candidat (Un seul par User)
# =========================
class Candidat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="candidat")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    telephone = models.CharField(max_length=20, blank=True)
    cv = models.FileField(upload_to="cvs/", blank=True, null=True)
    skills = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


# =========================
# Offre
# =========================
class Offre(models.Model):
    recruteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offres")
    titre = models.CharField(max_length=255)
    description = models.TextField()
    competences = models.TextField(help_text="Compétences séparées par des virgules")
    date_publication = models.DateTimeField(default=timezone.now)
    date_expiration = models.DateField()
    lieu = models.CharField(max_length=255)
    salaire = models.CharField(max_length=50)

    def __str__(self):
        return self.titre

    def est_active(self):
        return timezone.now().date() <= self.date_expiration


# =========================
# Postulation
# =========================
class Postulation(models.Model):
    class Status(models.TextChoices):
        RECUE = "RECUE", "Reçue"
        QUALIFIEE = "QUALIFIEE", "Qualifiée"
        ENTRETIEN = "ENTRETIEN", "Entretien"
        REFUSEE = "REFUSEE", "Refusée"

    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name="postulations")
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE, related_name="postulations")
    date_postulation = models.DateTimeField(default=timezone.now)
    score = models.FloatField(null=True, blank=True)
    found_skills_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECUE)
    
    THRESHOLD = 70.0

    def __str__(self):
        return f"{self.candidat} -> {self.offre} ({self.score if self.score is not None else 'NA'})"

    def update_status_from_score(self):
        if self.score is None:
            return
        if self.status in [self.Status.ENTRETIEN, self.Status.REFUSEE]:
            return
        self.status = self.Status.QUALIFIEE if self.score >= self.THRESHOLD else self.Status.RECUE

    def save(self, *args, **kwargs):
        self.update_status_from_score()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["candidat", "offre"], name="uniq_postulation_candidat_offre")
        ]
        indexes = [
            models.Index(fields=["offre", "status"]),
            models.Index(fields=["score"]),
        ]


# =========================
# Entretien
# =========================
class Entretien(models.Model):
    MODE_CHOICES = [
        ("VISIO", "Visio"),
        ("PRESENTIEL", "Présentiel"),
    ]

    postulation = models.OneToOneField(Postulation, on_delete=models.CASCADE, related_name="entretien")
    scheduled_at = models.DateTimeField()
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="VISIO")
    link_or_address = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entretien - {self.postulation.candidat} ({self.postulation.offre})"

    def save(self, *args, **kwargs):
        if self.postulation.status != Postulation.Status.ENTRETIEN:
            self.postulation.status = Postulation.Status.ENTRETIEN
            self.postulation.save(update_fields=["status"])
        super().save(*args, **kwargs)