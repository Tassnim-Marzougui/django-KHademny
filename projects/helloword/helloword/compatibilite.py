# helloword/compatibilite.py

import os
from docx import Document
from PyPDF2 import PdfReader
import spacy

# Charger modèle français
try:
    nlp = spacy.load("fr_core_news_md")
except OSError:
    nlp = spacy.load("fr_core_news_sm")  # fallback

# Extraction texte CV
def extract_text_cv(cv_path):
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
        raise ValueError("Format non supporté (DOCX ou PDF uniquement)")

# Compatibilité SpaCy
def evaluer_compatibilite(cv_path, competences_requises):
    """
    Renvoie : score (0-100), niveau (Faible/Moyen/Élevé), compétences trouvées
    """
    text = extract_text_cv(cv_path)
    doc_cv = nlp(text)

    competences_trouvees = []
    for skill in competences_requises:
        doc_skill = nlp(skill)
        if doc_cv.similarity(doc_skill) > 0.65:  # seuil ajustable
            competences_trouvees.append(skill)

    score = (len(competences_trouvees) / len(competences_requises)) * 100 if competences_requises else 0

    if score >= 70:
        niveau = "Élevé"
    elif score >= 40:
        niveau = "Moyen"
    else:
        niveau = "Faible"

    return score, niveau, competences_trouvees
