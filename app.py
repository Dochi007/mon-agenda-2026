import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, json, io

# --- CONFIGURATION ---
st.set_page_config(page_title="Mon Agenda 2026", layout="wide")

# --- CSS GOOGLE STYLE (Adaptatif) ---
st.markdown("""
    <style>
    /* Masquer les menus Streamlit pour faire "App" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style des cartes jours pour le mode liste (Mobile) */
    .day-card {
        background-color: white;
        border-left: 5px solid #1a73e8;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .day-label { font-weight: bold; color: #3c4043; font-size: 1.1rem; }
    
    /* Pastilles d'évènements */
    .event-tag {
        color: white; padding: 4px 10px; border-radius: 15px; 
        font-size: 12px; margin-top: 5px; display: inline-block;
        font-weight: 500;
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

# --- BARRE DE NAVIGATION ---
st.title("📅 Agenda 2026")
mois_sel = st.selectbox("Mois actuel", list(CONFIG_2026.keys()), index=3)
params = CONFIG_2026[mois_sel]

# Sélecteur de vue (Auto-détection simplifiée)
vue = st.radio("Format d'affichage", ["📱 Liste (Mobile)", "🖥️ Grille (Ordinateur)"], horizontal=True)

# --- ZONE D'AJOUT RAPIDE ---
with st.expander("➕ Ajouter un évènement", expanded=False):
    c1, c2 = st.columns(2)
    d_input = c1.number_input("Jour", 1, params["jours"])
    o_input = c2.selectbox("Organisateur", list(ORGANISATEURS.keys()))
    t_input = st.text_input("Description de l'évènement")
    if st.button("Enregistrer dans l'agenda", use_container_width=True):
        if d_input not in st.session_state.activites: st.session_state.activites[d_input] = []
        st.session_state.activites[d_input].append({"texte": f"{o_input} - {t_input}", "couleur": ORGANISATEURS[o_input]})
        st.rerun()

st.divider()

# --- AFFICHAGE ---
if vue == "📱 Liste (Mobile)":
    # Affichage en liste verticale (comme Google Calendar Planning)
    for j in range(1, params["jours"] + 1):
        # On n'affiche que les jours qui ont des évènements (ou tous, au choix)
        # Ici on affiche tous les jours pour pouvoir cliquer dessus
        st.markdown(f"""<div class="day-card"><span class="day-label">Jour {j}</span></div>""", unsafe_allow_html=True)
        
        if j in st.session_state.activites:
            for ev in st.session_state.activites[j]:
                c = ev['couleur']
                st.markdown(f'<div class="event-tag" style="background-color:rgb({c[0]},{c[1]},{c[2]});">{ev["texte"]}</div>', unsafe_allow_html=True)
        
        # Petit bouton discret pour ajouter directement à ce jour
        if st.button("Ajouter", key=f"add_mob_{j}", size="small"):
            st.warning("Remonte en haut pour remplir le formulaire !")

else:
    # Affichage en grille classique pour ordinateur
    cols = st.columns(7)
    jours_sem = ["DIM", "LUN", "MAR", "MER", "JEU", "VEN", "SAM"]
    for i, d in enumerate(jours_sem): cols[i].markdown(f"<center><b>{d}</b></center>", unsafe_allow_html=True)
    
    decalage = params["decalage"]
    for i in range(42):
        c_idx = i % 7
        j_num = i - decalage + 1
        with cols[c_idx]:
            if 1 <= j_num <= params["jours"]:
                st.markdown(f'<div style="border:1px solid #eee; height:80px; padding:5px;"><b>{j_num}</b></div>', unsafe_allow_html=True)
                if j_num in st.session_state.activites:
                    for ev in st.session_state.activites[j_num]:
                        c = ev['couleur']
                        st.markdown(f'<div style="background-color:rgb({c[0]},{c[1]},{c[2]}); color:white; font-size:10px; padding:2px; border-radius:3px; margin-bottom:2px;">{ev["texte"]}</div>', unsafe_allow_html=True)

# --- EXPORT ---
st.sidebar.divider()
if st.sidebar.button("🖼️ GÉNÉRER L'IMAGE JPEG HD", use_container_width=True):
    # Ta fonction de dessin PIL génère toujours le format Grille HD pour le Bureau
    st.sidebar.success("L'image est prête au téléchargement en bas de page !")
