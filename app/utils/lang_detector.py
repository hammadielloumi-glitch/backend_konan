from langdetect import detect

def detect_language(text: str) -> str:
    """
    Détecte la langue du texte fourni.
    Retourne 'fr', 'ar' ou 'tn' (dialecte tunisien par défaut).
    """
    try:
        lang = detect(text)
        if lang.startswith("ar"):
            return "ar"
        elif lang.startswith("fr"):
            return "fr"
        else:
            return "tn"
    except:
        return "fr"
