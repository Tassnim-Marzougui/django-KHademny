from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .utils import normalize_text

def calculer_match_cv_offre(cv_text, skills):
    cv_text_norm = normalize_text(cv_text)
    vectorizer = TfidfVectorizer().fit([cv_text_norm] + skills)

    found = []
    for skill in skills:
        tfidf_matrix = vectorizer.transform([cv_text_norm, skill])
        sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        if sim > 0.4:
            found.append(skill)

    score = round((len(found) / len(skills)) * 100, 2) if skills else 0

    return score, found
