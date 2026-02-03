import textract

# 🟢 Remplace ce chemin par le vrai chemin de ton fichier CV
cv_path = r"C:\Users\HP\Desktop\ing4\django\tas\projects\helloword\cv.docx"

# 🔹 Extraction du texte avec textract
text = textract.process(cv_path, encoding='utf-8')

# 🔹 Affichage du contenu extrait
print(text.decode('utf-8'))
