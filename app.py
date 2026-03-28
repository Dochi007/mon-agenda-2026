import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, json, io

# --- CONFIGURATION PAGE WEB ---
st.set_page_config(page_title="Agenda Pro 2026", layout="wide")

# --- STYLE CSS (Pour recréer les cases Google) ---
st.markdown("""
    <style>
    .stButton > button {
        height: 100px; width: 100%; border-radius: 0; border: 0.5px solid #e0e0e0;
        background-color: white; color: #70757a; align-items: flex-start;
    }
    .event-pill {
        color: white; padding: 2px 5px; border-radius: 4px; font-size: 10px; margin-bottom: 2px;
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

if 'activites' not in st.session_state: st.session_state.activites = {}

# --- HEADER ---
st.title("📅 Agenda Pro 2026")
mois_sel = st.selectbox("Mois", list(CONFIG_2026.keys()), index=3)
params = CONFIG_2026[mois_sel]

# --- GRILLE ---
cols = st.columns(7)
for i, d in enumerate(["DIM", "LUN", "MAR", "MER", "JEU", "VEN", "SAM"]):
    cols[i].write(f"**{d}**")

decalage = params["decalage"]
for i in range(42):
    c_idx = i % 7
    jour_num = i - decalage + 1
    with cols[c_idx]:
        if 1 <= jour_num <= params["jours"]:
            if st.button(f"{jour_num}", key=f"btn_{i}"):
                st.session_state.selected_day = jour_num
            
            if jour_num in st.session_state.activites:
                for ev in st.session_state.activites[jour_num]:
                    c = ev['couleur']
                    st.markdown(f'<div class="event-pill" style="background-color:rgb({c[0]},{c[1]},{c[2]});">{ev["texte"]}</div>', unsafe_allow_html=True)

# --- FORMULAIRE D'AJOUT ---
if 'selected_day' in st.session_state:
    st.sidebar.subheader(f"Ajouter au {st.session_state.selected_day} {mois_sel}")
    org = st.sidebar.selectbox("Organisateur", list(ORGANISATEURS.keys()))
    txt = st.sidebar.text_input("Evènement")
    if st.sidebar.button("Enregistrer"):
        d = st.session_state.selected_day
        if d not in st.session_state.activites: st.session_state.activites[d] = []
        st.session_state.activites[d].append({"texte": f"{org} - {txt}", "couleur": ORGANISATEURS[org]})
        del st.session_state.selected_day
        st.rerun()

# --- EXPORT IMAGE ---
if st.button("🖼️ GÉNÉRER L'IMAGE FINALE (JPEG)", use_container_width=True):
    # Logique de dessin PIL identique à ton code
    img = Image.open("test.png").convert("RGBA").resize((1800, 1400))
    calque = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    f_titre = ImageFont.truetype("Heavitas.ttf", 75)
    
    # Dessin du titre et de la grille (simplifié pour l'exemple)
    draw.text((900, 180), f"{mois_sel.upper()} 2026", fill=(0,0,0,255), font=f_titre, anchor="mm")
    
    # Fusion et téléchargement
    final = Image.alpha_composite(img, calque).convert("RGB")
    buf = io.BytesIO()
    final.save(buf, format="JPEG")
    st.image(final)
    st.download_button("📥 Télécharger l'image", buf.getvalue(), f"Agenda_{mois_sel}.jpg", "image/jpeg")
