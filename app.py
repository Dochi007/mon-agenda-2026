import streamlit as st
from streamlit_calendar import calendar
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Programmation EEF", layout="wide")

# --- DONNÉES ---
ORGANISATEURS = {
    "EEF": {"rgb": (52, 168, 83, 255), "hex": "#34a853"},
    "JFC": {"rgb": (161, 66, 244, 255), "hex": "#a142f4"},
    "JE":  {"rgb": (217, 48, 37, 255), "hex": "#d93025"},
    "DC":  {"rgb": (249, 171, 0, 255), "hex": "#f9ab00"}
}

MOIS_NUM = {"Janvier": "01", "Février": "02", "Mars": "03", "Avril": "04", "Mai": "05", "Juin": "06", 
            "Juillet": "07", "Août": "08", "Septembre": "09", "Octobre": "10", "Novembre": "11", "Décembre": "12"}

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
mois_sel = st.selectbox("Mois", list(CONFIG_2026.keys()), index=3)
params = CONFIG_2026[mois_sel]
m_num = MOIS_NUM[mois_sel]

# --- AJOUT RAPIDE ---
with st.expander("➕ Ajouter un évènement", expanded=True):
    c1, c2, c3 = st.columns([1, 2, 3])
    d_input = c1.number_input("Jour", 1, params["jours"])
    o_input = c2.selectbox("Organisateur", list(ORGANISATEURS.keys()))
    t_input = c3.text_input("Titre")
    if st.button("Enregistrer", use_container_width=True):
        if d_input not in st.session_state.activites: st.session_state.activites[d_input] = []
        st.session_state.activites[d_input].append({"texte": f"{o_input} - {t_input}", "couleur": ORGANISATEURS[o_input]["rgb"]})
        if 'image_export' in st.session_state: del st.session_state['image_export']
        st.rerun()

# --- CALENDRIER INTERACTIF (Type Google) ---
calendar_events = []
for jour, evs in st.session_state.activites.items():
    jour_str = f"{jour:02d}"
    for ev in evs:
        hex_col = "#1a73e8"
        for k, v in ORGANISATEURS.items():
            if v["rgb"] == ev["couleur"]: hex_col = v["hex"]
            
        calendar_events.append({
            "title": ev["texte"],
            "start": f"2026-{m_num}-{jour_str}",
            "color": hex_col
        })

calendar_options = {
    "initialView": "dayGridMonth",
    "initialDate": f"2026-{m_num}-01",
    "locale": "fr",
    "headerToolbar": {"left": "", "center": "title", "right": ""},
    "height": 600
}

calendar(events=calendar_events, options=calendar_options)

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
        f_leg = ImageFont.load_default(size=22)
    except:
        f_titre = f_num = f_ev = f_leg = ImageFont.load_default()

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

    x_leg = grid_x + (total_w - (len(ORGANISATEURS) * 220)) // 2 + 60
    y_leg = grid_y + (6 * row_h) + 20
    
    for i, (nom, conf) in enumerate(ORGANISATEURS.items()):
        x_p = x_leg + (i * 220)
        d.rectangle([x_p, y_leg, x_p+30, y_leg+30], fill=conf["rgb"])
        d.text((x_p + 40, y_leg + 2), nom, fill=(50,50,50,255), font=f_leg)

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
