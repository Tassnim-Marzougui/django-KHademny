from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(cv_text, job_skills):
    # Transformer les deux textes en vecteurs TF-IDF
    vectorizer = TfidfVectorizer().fit([cv_text, job_skills])
    matrix = vectorizer.transform([cv_text, job_skills])

    # Calculer la similarité cosinus
    score = cosine_similarity(matrix[0], matrix[1])[0][0]

    # convertir numpy.float64 → float normal
    return float(score)
