# --- CHARGEMENT INTELLIGENT DES POLICES ---
    def charger_police(nom_fichier, taille):
        # On essaie d'abord la police fournie, puis les polices standards du serveur Streamlit
        chemins = [
            nom_fichier,
            "Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
        for chemin in chemins:
            try:
                return ImageFont.truetype(chemin, taille)
            except IOError:
                continue
        return ImageFont.load_default()

    # On utilise la nouvelle fonction (Mettez "Arial.ttf" si vous l'avez ajouté à GitHub)
    f_titre = charger_police("Heavitas.ttf", 75)
    f_num = charger_police("Arial.ttf", 30)
    f_ev = charger_police("Arial.ttf", 18)
    f_leg = charger_police("Arial.ttf", 22)
