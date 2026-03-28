import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, json, io

# --- CONFIGURATION ---
st.set_page_config(page_title="Agenda Mobile 2026", layout="wide")

# --- CSS ADAPTATIF (MOBILE & PC) ---
st.markdown("""
    <style>
    /* Sur PC : 7 colonnes / Sur Mobile : Adaptation automatique */
    @media (max-width: 800px) {
        .main .block-container { padding: 0.5rem; }
        h1 { font-size: 1.5rem !important; }
        .stButton > button {
            height: 80px !important; /* Cases plus petites sur mobile */
            font-size: 14px !important;
        }
    }
    
    /* Style des pastilles pour mobile */
    .event-pill {
        color: white;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 9px;
        margin-top: 1px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES ---
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

# --- INTERFACE MOBILE ---
st.title(f"📅 Agenda 2026")

mois_sel = st.selectbox("Mois", list(CONFIG_2026.keys()), index=3)
params = CONFIG_2026[mois_sel]

# Sur mobile, on utilise souvent un bouton d'ajout rapide en haut
with st.expander("➕ Ajouter un évènement"):
    col_day, col_org = st.columns(2)
    day_add = col_day.number_input("Jour", 1, params["jours"])
    org_add = col_org.selectbox("Qui ?", list(ORGANISATEURS.keys()))
    txt_add = st.text_input("Description")
    if st.button("Enregistrer"):
        if day_add not in st.session_state.activites: st.session_state.activites[day_add] = []
        st.session_state.activites[day_add].append({"texte": f"{org_add} - {txt_add}", "couleur": ORGANISATEURS[org_add]})
        st.rerun()

# --- GRILLE ADAPTATIVE ---
# On définit le nombre de colonnes selon la largeur (Streamlit gère ça via st.columns)
n_cols = 7 
cols = st.columns(n_cols)

jours_semaine = ["DI", "LU", "MA", "ME", "JE", "VE", "SA"]
for i, d in enumerate(jours_semaine):
    cols[i].markdown(f"**{d}**")

decalage = params["decalage"]
for i in range(42):
    c_idx = i % 7
    jour_num = i - decalage + 1
    
    with cols[c_idx]:
        if 1 <= jour_num <= params["jours"]:
            # Sur mobile, le bouton est plus compact
            if st.button(f"{jour_num}", key=f"m_btn_{i}", use_container_width=True):
                st.toast(f"Jour {jour_num} sélectionné")
            
            if jour_num in st.session_state.activites:
                for ev in st.session_state.activites[jour_num]:
                    c = ev['couleur']
                    st.markdown(f'<div class="event-pill" style="background-color:rgb({c[0]},{c[1]},{c[2]});">{ev["texte"]}</div>', unsafe_allow_html=True)
        else:
            st.write("")

# --- BOUTON EXPORT ---
st.divider()
if st.button("🖼️ GÉNÉRER L'IMAGE HD", use_container_width=True):
    # (Ici ton code de dessin PIL pour l'image finale sur le Bureau/Download)
    st.info("L'image HD sera générée avec le format paysage classique.")
