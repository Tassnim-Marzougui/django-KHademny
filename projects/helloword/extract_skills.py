import textract
import re

# Chemin vers le CV (PDF, DOCX, TXT...)
cv_path = r"C:\Users\HP\Desktop\ing4\django\tas\projects\helloword\cv.docx"

# Extraire le texte du CV et le normaliser en minuscules
text = textract.process(cv_path).decode("utf-8").lower()

# Exemple d'offre d'emploi pour un test
offre_emploi = {
    "titre": "Développeur Full Stack",
    "description": """
    Nous recherchons un développeur expérimenté maîtrisant Python, Django, SQL,
    Java, JavaScript, React, Node.js et Agile.
    La connaissance de PostgreSQL et MongoDB est un plus.
    """
}

# Extraire dynamiquement les compétences depuis l'offre
competences = ["Python", "Django", "SQL", "Java", "JavaScript", "React", "Node.js", "Agile", "PostgreSQL", "MongoDB"]

# Normaliser en minuscules
competences_lower = [c.lower() for c in competences]

# Chercher les compétences présentes dans le CV
found_skills = [skill for skill in competences_lower if re.search(rf"\b{re.escape(skill)}\b", text)]

# Calculer le score de compatibilité en %
if competences_lower:
    score_percent = round(len(found_skills) / len(competences_lower) * 100, 2)
else:
    score_percent = 0.0

# Affichage
print("Compétences trouvées :", found_skills)
print(f"Score compatibilité : {score_percent}%")

# Vérification seuil (>70% = Acceptable)
SEUIL_ACCEPTABLE = 70
if score_percent >= SEUIL_ACCEPTABLE:
    print("✅ CV compatible avec l'offre")
else:
    print("⚠️ CV faible compatibilité avec l'offre")
