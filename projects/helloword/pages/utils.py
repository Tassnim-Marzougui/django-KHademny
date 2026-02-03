import re
import docx
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_cv_text(file_path):
    """
    Extrait le texte d'un CV (PDF ou DOCX).
    """
    text = ""
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file_path.lower().endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise ValueError("Format non supporté (seulement PDF ou DOCX)")
    return text


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9àâçéèêëîïôûùüÿñ\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculer_match_cv_offre(cv_text, offer_skills):
    cv_lower = cv_text.lower()
    found_skills = [skill for skill in offer_skills if skill in cv_lower]

    # ✅ Score basé sur proportion de compétences trouvées
    if offer_skills:
        score = round(len(found_skills) / len(offer_skills) * 100, 2)
    else:
        score = 0.0

    return score, found_skills
