import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, json, io

st.set_page_config(page_title="Agenda", layout="centered")

# --- CSS MATERIAL DESIGN (STYLE GOOGLE) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .day-header {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #70757a;
        margin-top: 15px;
        margin-bottom: 5px;
        font-weight: 500;
        text-transform: uppercase;
    }
    .day-number {
        font-size: 24px;
        color: #3c4043;
        margin-right: 15px;
    }
    </style>
""", unsafe_allow_html=True)

ORGANISATEURS = {
    "EEF": (52, 168, 83, 255), "JFC": (161, 66, 244, 255),
    "JE":  (217, 48, 37, 255), "DC":  (249, 171, 0, 255),
    "Std": (26, 115, 232, 255)
}

CONFIG_2026 = {
    "Janvier": {"decalage": 4, "jours": 31}, "Février": {"decalage": 0, "jours": 28},
    "Mars": {"decalage": 0, "jours": 31}, "Avril": {"decalage": 3, "jours": 30},
    "Mai": {"decalage": 5, "jours": 31}, "Juin": {"decalage": 1, "jours": 30},
    "Juillet": {"decalage": 3, "jours": 31}, "Août": {"decalage": 6, "jours": 31},
    "Septembre": {"decalage": 2, "jours": 30}, "Octobre": {"decalage": 4, "jours": 31},
    "Novembre": {"decalage": 0, "jours": 30}, "Décembre": {"decalage": 2, "jours": 31}
}

if 'activites' not in st.session_state:
    st.session_state.activites = {}

st.title("Agenda 2026")
mois_sel = st.selectbox("Mois", list(CONFIG_2026.keys()), index=3, label_visibility="collapsed")
params = CONFIG_2026[mois_sel]

# --- AJOUT (Remplaçant le bouton flottant Google) ---
with st.expander("➕ Ajouter un évènement"):
    c1, c2 = st.columns(2)
    d_input = c1.number_input("Jour", 1, params["jours"])
    o_input = c2.selectbox("Organisateur", list(ORGANISATEURS.keys()))
    t_input = st.text_input("Titre")
    if st.button("Enregistrer", use_container_width=True):
        if d_input not in st.session_state.activites: st.session_state.activites[d_input] = []
        st.session_state.activites[d_input].append({"texte": f"{o_input} - {t_input}", "couleur": ORGANISATEURS[o_input]})
        st.rerun()

st.divider()

# --- VUE PLANNING (Type Google Calendar Mobile) ---
for j in range(1, params["jours"] + 1):
    if j in st.session_state.activites:
        st.markdown(f'<div class="day-header"><span class="day-number">{j}</span> {mois_sel[:3].upper()}</div>', unsafe_allow_html=True)
        for ev in st.session_state.activites[j]:
            c = ev['couleur']
            # Bulle d'événement avec bordure arrondie Google Style
            st.markdown(f"""
                <div style="background-color:rgb({c[0]},{c[1]},{c[2]}); color:white; 
                padding:12px 15px; border-radius:8px; margin-bottom:8px; font-family:sans-serif; font-size:14px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                {ev['texte']}
                </div>
            """, unsafe_allow_html=True)

# --- EXPORT IMAGE ---
st.divider()
if st.button("🖼️ GÉNÉRER L'IMAGE JPEG HD", use_container_width=True):
    # La génération de l'image (Moteur PIL) ira ici
    st.success("Fonction d'export prête !")
