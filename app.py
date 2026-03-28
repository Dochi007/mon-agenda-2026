import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, json, io

st.set_page_config(page_title="Programmation EEF", layout="centered")

# --- CSS MATERIAL DESIGN ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .day-header { font-family: 'Roboto', sans-serif; font-size: 14px; color: #70757a; margin-top: 15px; margin-bottom: 5px; font-weight: 500; text-transform: uppercase; }
    .day-number { font-size: 24px; color: #3c4043; margin-right: 15px; }
    </style>
""", unsafe_allow_html=True)

ORGANISATEURS = {
    "EEF": (52, 168, 83, 255), "JFC": (161, 66, 244, 255),
    "JE":  (217, 48, 37, 255), "DC":  (249, 171, 0, 255)
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

st.title("Programmation EEF")
mois_sel = st.selectbox("Mois", list(CONFIG_2026.keys()), index=3, label_visibility="collapsed")
params = CONFIG_2026[mois_sel]

# --- AJOUT RAPIDE ---
with st.expander("➕ Ajouter un évènement"):
    c1, c2 = st.columns(2)
    d_input = c1.number_input("Jour", 1, params["jours"])
    o_input = c2.selectbox("Organisateur", list(ORGANISATEURS.keys()))
    t_input = st.text_input("Titre")
    if st.button("Enregistrer", use_container_width=True):
        if d_input not in st.session_state.activites: st.session_state.activites[d_input] = []
        st.session_state.activites[d_input].append({"texte": f"{o_input} - {t_input}", "couleur": ORGANISATEURS[o_input]})
        # Effacer l'image en cache si on ajoute un nouvel événement
        if 'image_export' in st.session_state:
            del st.session_state['image_export']
        st.rerun()

st.divider()

# --- VUE MOBILE ---
for j in range(1, params["jours"] + 1):
    if j in st.session_state.activites:
        st.markdown(f'<div class="day-header"><span class="day-number">{j}</span> {mois_sel[:3].upper()}</div>', unsafe_allow_html=True)
        for ev in st.session_state.activites[j]:
            c = ev['couleur']
            st.markdown(f'<div style="background-color:rgb({c[0]},{c[1]},{c[2]}); color:white; padding:12px 15px; border-radius:8px; margin-bottom:8px; font-family:sans-serif; font-size:14px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">{ev["texte"]}</div>', unsafe_allow_html=True)

# --- MOTEUR DE DESSIN PIL ---
def generer_image_hd(mois, activites):
    p = CONFIG_2026[mois]
    base = Image.open("test.png").convert("RGBA").resize((1800, 1400))
    txt_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(txt_layer)
    
    try:
        f_titre = ImageFont.truetype("Heavitas.ttf", 75)
        f_num = ImageFont.load_default(size=30)
        f_ev = ImageFont.load_default(size=18)
    except:
        f_titre = f_num = f_ev = ImageFont.load_default()

    grid_x, grid_y, total_w, total_h = 110, 320, 1600, 1000
    col_w, row_h = total_w // 7, total_h // 6

    d.text((grid_x + total_w//2, grid_y - 140), f"{mois.upper()} 2026", fill=(0,0,0,255), font=f_titre, anchor="mm")

    for i in range(42):
        row, col = i // 7, i % 7
        j_num = i - p["decalage"] + 1
        x, y = grid_x + (col * col_w), grid_y + (row * row_h)
        
        if 1 <= j_num <= p["jours"]:
            d.rectangle([x+8, y+8, x+col_w-8, y+row_h-8], outline=(200, 200, 200, 255), width=2)
            d.text((x+col_w-25, y+35), str(j_num), fill=(80,80,80,255), font=f_num, anchor="rm")
            
            if j_num in activites:
                y_off = y + 75
                evs = activites[j_num]
                ch = min(35, (row_h - 90) // max(1, len(evs)) - 4)
                for ev in evs:
                    d.rounded_rectangle([x+15, y_off, x+col_w-15, y_off+ch], radius=6, fill=tuple(ev["couleur"]))
                    d.text((x + col_w//2, y_off + ch//2), ev["texte"], fill="white", font=f_ev, anchor="mm")
                    y_off += ch + 4

    return Image.alpha_composite(base, txt_layer).convert("RGB")

st.divider()

# --- BOUTON EXPORT ---
if st.button("🖼️ PRÉPARER L'IMAGE JPEG HD", use_container_width=True):
    with st.spinner("Dessin de l'image en cours..."):
        img_finale = generer_image_hd(mois_sel, st.session_state.activites)
        buf = io.BytesIO()
        img_finale.save(buf, format="JPEG", quality=95)
        st.session_state['image_export'] = buf.getvalue()

if 'image_export' in st.session_state:
    st.image(st.session_state['image_export'], caption="Aperçu du fichier final")
    st.download_button(
        label="📥 CLIQUER ICI POUR TÉLÉCHARGER",
        data=st.session_state['image_export'],
        file_name=f"Programmation_EEF_{mois_sel}_2026.jpg",
        mime="image/jpeg",
        use_container_width=True
    )
