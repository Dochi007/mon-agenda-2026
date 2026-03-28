import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import json
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Agenda Pro 2026", layout="wide")

ORGANISATEURS = {
    "EEF": (52, 168, 83, 178), "JFC": (161, 66, 244, 178),
    "JE":  (217, 48, 37, 178), "DC":  (249, 171, 0, 178),
    "Std": (26, 115, 232, 178)
}

CONFIG_2026 = {
    "Janvier": {"decalage": 4, "jours": 31}, "Février": {"decalage": 0, "jours": 28},
    "Mars": {"decalage": 0, "jours": 31}, "Avril": {"decalage": 3, "jours": 30},
    "Mai": {"decalage": 5, "jours": 31}, "Juin": {"decalage": 1, "jours": 30},
    "Juillet": {"decalage": 3, "jours": 31}, "Août": {"decalage": 6, "jours": 31},
    "Septembre": {"decalage": 2, "jours": 30}, "Octobre": {"decalage": 4, "jours": 31},
    "Novembre": {"decalage": 0, "jours": 30}, "Décembre": {"decalage": 2, "jours": 31}
}

# --- GESTION DES DONNÉES (Session State) ---
if 'activites' not in st.session_state:
    st.session_state.activites = {}

# --- INTERFACE LATÉRALE (SAISIE) ---
st.sidebar.title("🛠 Configuration")
mois_sel = st.sidebar.selectbox("Choisir le mois", list(CONFIG_2026.keys()))
params = CONFIG_2026[mois_sel]

with st.sidebar.expander("➕ Ajouter un évènement", expanded=True):
    jour = st.number_input("Jour", min_value=1, max_value=params["jours"], value=1)
    org = st.selectbox("Organisateur", list(ORGANISATEURS.keys()))
    texte = st.text_input("Description")
    if st.button("Ajouter à l'agenda"):
        if jour not in st.session_state.activites:
            st.session_state.activites[jour] = []
        st.session_state.activites[jour].append({"texte": f"{org} - {texte}", "couleur": ORGANISATEURS[org]})
        st.toast("Évènement ajouté !")

if st.sidebar.button("🗑 Effacer tout le mois"):
    st.session_state.activites = {}
    st.rerun()

# --- AFFICHAGE DU CALENDRIER (STYLE GOOGLE) ---
st.title(f"📅 {mois_sel.upper()} 2026")

# Création de la grille web
cols = st.columns(7)
jours_semaine = ["DIM", "LUN", "MAR", "MER", "JEU", "VEN", "SAM"]

for i, nom_j in enumerate(jours_semaine):
    cols[i].markdown(f"**{nom_j}**")

decalage = params["decalage"]
for i in range(42):
    col_idx = i % 7
    jour_num = i - decalage + 1
    
    with cols[col_idx]:
        if 1 <= jour_num <= params["jours"]:
            # Style de la case
            st.markdown(f"### {jour_num}")
            if jour_num in st.session_state.activites:
                for idx, ev in enumerate(st.session_state.activites[jour_num]):
                    c = ev['couleur']
                    st.markdown(f"""
                        <div style="background-color: rgba({c[0]},{c[1]},{c[2]},0.7); 
                        color: white; padding: 2px 5px; border-radius: 4px; font-size: 12px; margin-bottom: 2px;">
                        {ev['texte']}
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("")

# --- GÉNÉRATION DE L'IMAGE ---
st.divider()
if st.button("🚀 GÉNÉRER L'IMAGE HD (JPEG)", use_container_width=True):
    # (Ici on place ta logique PIL de dessin, identique à avant)
    # Pour l'exemple, voici la sauvegarde dans un buffer pour téléchargement
    img_fond = Image.open("test.png").convert("RGBA").resize((1800, 1400))
    # ... [Ton code de dessin draw_c / draw_f ici] ...
    
    # Export final
    buf = io.BytesIO()
    img_fond.convert("RGB").save(buf, format="JPEG")
    st.download_button(
        label="📥 Télécharger l'image prête",
        data=buf.getvalue(),
        file_name=f"Agenda_{mois_sel}_2026.jpg",
        mime="image/jpeg"
    )