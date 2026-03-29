import streamlit as st
from streamlit_calendar import calendar
from PIL import Image, ImageDraw, ImageFont
import io
import calendar as cal_sys

st.set_page_config(page_title="Programmation EEF", layout="wide")

def charger_police(nom_fichier, taille):
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

ORGANISATEURS = {
    "EEF":   {"rgb": (52, 168, 83, 178), "hex": "#34a853"},
    "JFC":   {"rgb": (161, 66, 244, 178), "hex": "#a142f4"},
    "JE":    {"rgb": (217, 48, 37, 178), "hex": "#d93025"},
    "DC":    {"rgb": (249, 171, 0, 178), "hex": "#f9ab00"},
    "Kabod": {"rgb": (66, 133, 244, 178), "hex": "#4285f4"},
    "EP":    {"rgb": (255, 112, 67, 178), "hex": "#ff7043"}
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

def generer_tous_les_recurrents():
    tous_les_mois = {}
    for mois_nom, mois_num_str in MOIS_NUM.items():
        mois_num = int(mois_num_str)
        matrice = cal_sys.monthcalendar(2026, mois_num)
        
        vendredis = [semaine[4] for semaine in matrice if semaine[4] != 0]
        dernier_vendredi = vendredis[-1]
        samedis = [semaine[5] for semaine in matrice if semaine[5] != 0]
        premier_samedi = samedis[0]
        
        recurrents_du_mois = {}
        for semaine in matrice:
            for j_sem, jour in enumerate(semaine):
                if jour == 0: continue
                evs = []
                if j_sem == 0:   evs.append({"texte": "DC - Réunion", "couleur": ORGANISATEURS["DC"]["rgb"]})
                elif j_sem == 1: evs.append({"texte": "EEF - Service de prière", "couleur": ORGANISATEURS["EEF"]["rgb"]})
                elif j_sem == 2: evs.append({"texte": "EP - Réunion de prière", "couleur": ORGANISATEURS["EP"]["rgb"]})
                elif j_sem == 3: evs.append({"texte": "EEF - Etude biblique", "couleur": ORGANISATEURS["EEF"]["rgb"]})
                elif j_sem == 4:
                    if jour == dernier_vendredi: evs.append({"texte": "EEF - Veille de nuit", "couleur": ORGANISATEURS["EEF"]["rgb"]})
                elif j_sem == 5:
                    if jour == premier_samedi: evs.append({"texte": "EEF - Jeune et Sainte cène", "couleur": ORGANISATEURS["EEF"]["rgb"]})
                    else: evs.append({"texte": "Kabod - Répétition", "couleur": ORGANISATEURS["Kabod"]["rgb"]})
                elif j_sem == 6: evs.append({"texte": "EEF - Adoration", "couleur": ORGANISATEURS["EEF"]["rgb"]})
                    
                if evs: recurrents_du_mois[jour] = evs
        tous_les_mois[mois_nom] = recurrents_du_mois
    return tous_les_mois

if 'initialise' not in st.session_state:
    st.session_state.activites = generer_tous_les_recurrents()
    st.session_state.initialise = True
    st.session_state.last_action = None

@st.dialog("➕ Nouvel évènement")
def dialog_ajout(jour, mois):
    st.write(f"**Date :** {jour} {mois} 2026")
    o_input = st.selectbox("Organisateur", list(ORGANISATEURS.keys()))
    t_input = st.text_input("Titre")
    
    if st.button("Enregistrer", type="primary", use_container_width=True):
        if jour not in st.session_state.activites[mois]: st.session_state.activites[mois][jour] = []
        st.session_state.activites[mois][jour].append({"texte": f"{o_input} - {t_input}", "couleur": ORGANISATEURS[o_input]["rgb"]})
        if 'image_export' in st.session_state: del st.session_state['image_export']
        st.rerun()

@st.dialog("✏️ Supprimer l'évènement")
def dialog_supprimer(jour, mois, index_event, texte):
    st.write(f"Voulez-vous supprimer l'évènement : **{texte}** ?")
    if st.button("🗑️ Oui, Supprimer", type="primary", use_container_width=True):
        del st.session_state.activites[mois][jour][index_event]
        if len(st.session_state.activites[mois][jour]) == 0:
            del st.session_state.activites[mois][jour]
        if 'image_export' in st.session_state: del st.session_state['image_export']
        st.rerun()

st.title("Programmation EEF")
mois_sel = st.selectbox("Mois", list(CONFIG_2026.keys()), index=3)
params = CONFIG_2026[mois_sel]
m_num = MOIS_NUM[mois_sel]

st.info("💡 Cliquez directement sur une case du calendrier pour ajouter un évènement, ou sur un évènement pour le supprimer.")

calendar_events = []
for jour, evs in st.session_state.activites[mois_sel].items():
    jour_str = f"{jour:02d}"
    for ev in evs:
        hex_col = "#1a73e8"
        for k, v in ORGANISATEURS.items():
            if v["rgb"] == ev["couleur"]: hex_col = v["hex"]
        calendar_events.append({
            "title": ev["texte"],
            "start": f"2026-{m_num}-{jour_str}",
            "color": hex_col,
            "allDay": True
        })

calendar_options = {
    "initialView": "dayGridMonth",
    "initialDate": f"2026-{m_num}-01",
    "locale": "fr",
    "headerToolbar": {"left": "title", "center": "", "right": ""},
    "height": 600,
    "selectable": True
}

cal_result = calendar(events=calendar_events, options=calendar_options, callbacks=['dateClick', 'eventClick'])

if cal_result and "callback" in cal_result:
    callback_type = cal_result.get("callback")
    action_sig = str(cal_result)
    
    if st.session_state.last_action != action_sig:
        st.session_state.last_action = action_sig
        
        if callback_type == "dateClick":
            click_data = cal_result.get("dateClick", {})
            date_str = click_data.get("dateStr") or click_data.get("date", "")
            if date_str:
                jour_clique = int(date_str.split("T")[0].split("-")[2])
                dialog_ajout(jour_clique, mois_sel)
                
        elif callback_type == "eventClick":
            event_data = cal_result.get("eventClick", {}).get("event", {})
            event_title = event_data.get("title", "")
            event_start = event_data.get("start", "")
            if event_title and event_start:
                jour_clique = int(event_start.split("T")[0].split("-")[2])
                for idx, ev in enumerate(st.session_state.activites[mois_sel].get(jour_clique, [])):
                    if ev["texte"] == event_title:
                        dialog_supprimer(jour_clique, mois_sel, idx, event_title)
                        break

def largeur_texte(texte, font, draw):
    try:
        return draw.textlength(texte, font=font)
    except AttributeError:
        try:
            return draw.textbbox((0,0), texte, font=font)[2]
        except Exception:
            return len(texte) * 8

def tronquer_texte(texte, font, draw, max_largeur):
    if largeur_texte(texte, font, draw) <= max_largeur:
        return texte
    while len(texte) > 0 and largeur_texte(texte + "...", font, draw) > max_largeur:
        texte = texte[:-1]
    return texte + "..."

def generer_image_hd(mois, activites_du_mois):
    p = CONFIG_2026[mois]
    base = Image.open("test.png").convert("RGBA").resize((1800, 1400))
    txt_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(txt_layer)
    
    f_titre = charger_police("Heavitas.ttf", 75)
    f_num = charger_police("Arial.ttf", 30)
    f_ev = charger_police("Arial.ttf", 18)

    grid_x, grid_y, total_w, total_h = 110, 320, 1600, 1000
    col_w, row_h = total_w // 7, total_h // 6

    d.text((grid_x + total_w//2, grid_y - 140), f"{mois.upper()} 2026", fill=(0,0,0,255), font=f_titre, anchor="mm")

    for i in range(42):
        row, col = i // 7, i % 7
        j_num = i - p["decalage"] + 1
        x, y = grid_x + (col * col_w), grid_y + (row * row_h)
        
        if 1 <= j_num <= p["jours"]:
            # Cases avec marges réduites (+4 et -4 au lieu de +8 et -8)
            d.rounded_rectangle([x+4, y+4, x+col_w-4, y+row_h-4], radius=10, fill=(255, 255, 255, 255), outline=(200, 200, 200, 255), width=2)
            
            # Numéro du jour repoussé dans le coin en haut à droite (x+col_w-15, y+20)
            d.text((x+col_w-15, y+20), str(j_num), fill=(52, 168, 83, 255), font=f_num, anchor="rm")
            
            if j_num in activites_du_mois:
                # Le texte commence beaucoup plus haut (y+45 au lieu de y+75)
                y_off = y + 45
                evs = activites_du_mois[j_num]
                ch = min(35, (row_h - 55) // max(1, len(evs)) - 4)
                max_w = col_w - 20
                
                for ev in evs:
                    texte_propre = tronquer_texte(ev["texte"], f_ev, d, max_w)
                    d.text((x + col_w//2, y_off + ch//2), texte_propre, fill=(0,0,0,255), font=f_ev, anchor="mm")
                    y_off += ch + 4

    return Image.alpha_composite(base, txt_layer).convert("RGB")

st.divider()

if st.button("🖼️ PRÉPARER L'IMAGE JPEG HD", use_container_width=True):
    with st.spinner("Dessin de l'image en cours..."):
        img_finale = generer_image_hd(mois_sel, st.session_state.activites[mois_sel])
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
