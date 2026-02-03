import re
import unicodedata
from docx import Document
from PyPDF2 import PdfReader
import os

def normalize_text(text):
    """Supprime accents, ponctuation et met en minuscule"""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # supprime ponctuation
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_text_cv(cv_path):
    """Extrait le texte d'un CV (DOCX ou PDF)"""
    ext = os.path.splitext(cv_path)[1].lower()
    if ext == ".docx":
        doc = Document(cv_path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ext == ".pdf":
        reader = PdfReader(cv_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    else:
        raise ValueError("Format de fichier non supporté. Utilisez DOCX ou PDF.")

def evaluer_compatibilite(cv_path, competences_requises):
    text = extract_text_cv(cv_path)
    print("=== TEXTE BRUT DU CV ===")
    print(repr(text[:500]))   # affiche les 500 premiers caractères

    text = normalize_text(text)
    print("=== TEXTE NORMALISÉ ===")
    print(repr(text[:500]))

    words = set(text.split())
    competences_norm = [normalize_text(skill) for skill in competences_requises]
    print("=== COMPÉTENCES NORMALISÉES ===")
    print(competences_norm)

    competences_trouvees = []
    for skill in competences_norm:
        for word in skill.split():
            if word in words:
                competences_trouvees.append(skill)
                break

    score = (len(competences_trouvees) / len(competences_norm)) * 100 if competences_norm else 0

    if score >= 70:
        niveau = "Élevée"
    elif score >= 40:
        niveau = "Moyenne"
    else:
        niveau = "Faible"

    print(f"⚠️ Score compatibilité : {score:.1f}% → {niveau}")
    print("Compétences trouvées :", competences_trouvees)

    return score, niveau, competences_trouvees
