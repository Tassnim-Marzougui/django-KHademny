import os
import django

# --- LIGNE CORRIGÉE ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helloword.settings')
# -----------------------

django.setup()

from django.contrib.auth.models import User
from pages.models import Candidat


def fix_duplicate_candidates():
    print("Recherche des candidats dupliqués...")
    
    # Trouver tous les utilisateurs avec plusieurs candidats
    users_with_duplicates = []
    for user in User.objects.all():
        candidate_count = Candidat.objects.filter(user=user).count()
        if candidate_count > 1:
            users_with_duplicates.append(user)
            print(f"User {user.username} a {candidate_count} candidats")

    if not users_with_duplicates:
        print("Aucun utilisateur avec des candidats dupliqués trouvé.")
        return

    # Nettoyer les doublons
    for user in users_with_duplicates:
        # Obtenir tous les candidats pour cet utilisateur, ordonnés par ID
        candidates = Candidat.objects.filter(user=user).order_by('id')
        
        # Garder le premier et supprimer le reste
        keep_candidate = candidates.first()
        print(f"Garde du candidat {keep_candidate.id} pour l'utilisateur {user.username}")
        
        # Supprimer les doublons
        for candidate in candidates[1:]:
            print(f"Suppression du candidat dupliqué {candidate.id}")
            candidate.delete()

    print("Nettoyage terminé!")

if __name__ == "__main__":
    fix_duplicate_candidates()