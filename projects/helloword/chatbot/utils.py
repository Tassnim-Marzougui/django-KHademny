from pages.models import Offre, Candidat
from datetime import date

def handle_message(msg: str) -> str:
    msg = msg.lower().strip()

    # =======================
    # 👋 SALUTATION
    # =======================
    greetings = ["bonjour", "salem", "salut", "hello", "ahla", "cc", "bonsoir"]
    if any(word in msg for word in greetings):
        return (
            "👋 Bonjour ! Je suis l’assistant *Khademny*.\n"
            "Tu peux me demander :\n"
            "• Les dernières offres 💼\n"
            "• Comment postuler ✍️\n"
            "• Conseils CV 📄\n"
            "• Infos recruteurs 🧑‍💼\n\n"
            "نحن نفتح لك باب الأمل و نوافذ المستقبل 🌟"
        )

    # =======================
    # ℹ️ Infos sur la plateforme
    # =======================
    site_keywords = ["site", "plateforme", "application", "khademny", "c'est quoi", "comment fonctionne"]
    if any(word in msg for word in site_keywords):
        return (
            "🌐 *Khademny* est une plateforme RH qui connecte candidats et recruteurs.\n"
            "👉 Candidats : voir offres, déposer CV, postuler.\n"
            "👉 Recruteurs : publier offres, gérer candidatures.\n"
            "🎯 Objectif : connecter talents et opportunités 💼."
        )

    # =======================
    # 📰 Dernières offres
    # =======================
    if any(word in msg for word in ["offre", "emploi", "job", "poste", "travail"]):
        offres = Offre.objects.order_by("-id")[:3]
        if not offres:
            return "Aucune offre disponible pour le moment 💼."

        texte = "📌 *Dernières offres disponibles* :\n\n"
        for o in offres:
            texte += f"• **{o.titre}** – {o.lieu} (Expire le {o.date_expiration})\n"

        texte += "\nTu peux demander : *Détails salaire*, *comment postuler*, ou *offre + ID*."
        return texte

    # =======================
    # 📊 Détails salaires et dates
    # =======================
    if any(word in msg for word in ["salaire", "salaires", "combien", "date"]):
        offres = Offre.objects.order_by("-id")[:3]
        if not offres:
            return "Aucune offre disponible 💼."

        texte = "📊 *Détails des dernières offres* :\n"
        for o in offres:
            texte += (
                f"• {o.titre} | Salaire : {getattr(o, 'salaire', 'Non spécifié')} "
                f"| Expire : {o.date_expiration}\n"
            )
        return texte

    # =======================
    # ✍️ Comment postuler
    # =======================
    if "comment postuler" in msg or "postuler comment" in msg:
        return (
            "✍️ *Comment postuler à une offre :*\n"
            "1️⃣ Choisis une offre dans la liste.\n"
            "2️⃣ Clique sur **Postuler**.\n"
            "3️⃣ Remplis le formulaire candidat.\n"
            "4️⃣ Upload ton CV.\n"
            "5️⃣ Valide ta candidature.\n\n"
            "Si tu veux, je peux t’afficher les offres disponibles 👉 *offres*"
        )

    # "donner étape par étape"
    if "étape" in msg or "etape" in msg:
        return (
            "📝 *Étapes pour postuler sur Khademny :*\n"
            "1️⃣ Crée ton compte candidat.\n"
            "2️⃣ Complète ton profil.\n"
            "3️⃣ Choisis une offre.\n"
            "4️⃣ Clique sur **Postuler**.\n"
            "5️⃣ Télécharge ton CV.\n"
            "6️⃣ Suis ton dossier depuis ton tableau de bord.\n"
        )

    # =======================
    # 👔 Compte recruteur
    # =======================
    if "créer compte recruteur" in msg or "compte recruteur" in msg:
        return (
            "👔 *Créer un compte recruteur :*\n"
            "1️⃣ Va dans la section **Recruteur**.\n"
            "2️⃣ Clique sur **Créer un compte**.\n"
            "3️⃣ Remplis les infos de ton entreprise.\n"
            "4️⃣ Valide.\n"
            "5️⃣ Tu peux maintenant publier des offres 📝."
        )

    # =======================
    # 👤 Compte candidat
    # =======================
    if "créer compte" in msg or "compte candidat" in msg:
        return (
            "👤 *Créer un compte candidat :*\n"
            "1️⃣ Clique sur **S’inscrire**.\n"
            "2️⃣ Choisis **Candidat**.\n"
            "3️⃣ Entre email + mot de passe.\n"
            "4️⃣ Complète ton profil.\n"
            "5️⃣ Tu peux postuler immédiatement ✨."
        )

    # =======================
    # 📌 Postuler par ID
    # =======================
    if "postuler" in msg and any(c.isdigit() for c in msg):
        try:
            offre_id = int("".join([c for c in msg if c.isdigit()]))
            offre = Offre.objects.get(id=offre_id)
            return f"👉 Tu peux postuler à **{offre.titre}** via le bouton *Postuler*."
        except Offre.DoesNotExist:
            return "⚠️ Désolé, cette offre n’existe pas."

    # =======================
    # 👥 Nombre de candidats
    # =======================
    if "combien de candidats" in msg or "nombre de candidats" in msg:
        return f"👥 Il y a actuellement {Candidat.objects.count()} candidat(s)."

    # =======================
    # ⏳ Offres expirées
    # =======================
    if "offres expirées" in msg or "expiré" in msg:
        count = Offre.objects.filter(date_expiration__lt=date.today()).count()
        return f"⏳ {count} offre(s) ont expiré."

    # =======================
    # 🔍 Recherche par compétence
    # =======================
    skills = ["python", "django", "java", "react", "sql", "javascript", "php"]
    for skill in skills:
        if skill in msg:
            offres = (
                Offre.objects.filter(titre__icontains=skill) |
                Offre.objects.filter(description__icontains=skill)
            )
            if not offres:
                return f"Aucune offre trouvée pour *{skill}* ❌."

            texte = f"🔥 *Offres contenant {skill}* :\n"
            for o in offres:
                texte += f"• {o.titre} – {o.lieu} (Expire {o.date_expiration})\n"
            return texte

    # =======================
    # 📞 SUPPORT
    # =======================
    if "support" in msg or "contacter" in msg:
        return "📞 Contact support : support@khademny.com"

    # =======================
    # ❓ Réponse par défaut
    # =======================
    return (
        "🤔 Je n’ai pas compris ta demande.\n"
        "Essaie : *offres*, *salaire*, *postuler*, *candidat*, *recruteur*, *python*, *support*."
    )
