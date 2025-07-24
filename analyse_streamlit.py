import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import sqlite3
# streamlit run analyse_streamlit.py

# 

# --- Paramétrage fichier base ---
DB_FILE = "resultats_batiments.sqlite"

def create_or_open_db(dbfile=DB_FILE):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS validation (
            cleabs TEXT PRIMARY KEY,
            validation TEXT,
            commentaire TEXT DEFAULT NULL
        )
    ''')
    conn.commit()
    return conn

def set_validation(cleabs, validation, commentaire=None):
    conn = create_or_open_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO validation (cleabs, validation, commentaire)
        VALUES (?, ?, ?)
        ON CONFLICT(cleabs) DO UPDATE SET validation=excluded.validation, commentaire=excluded.commentaire
    ''', (cleabs, validation, commentaire))
    conn.commit()
    conn.close()

def get_validation(cleabs):
    conn = create_or_open_db()
    c = conn.cursor()
    c.execute('SELECT validation, commentaire FROM validation WHERE cleabs=?', (cleabs,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None, row[1] if row else None

def select_all_validations():
    conn = create_or_open_db()
    df = pd.read_sql_query("SELECT * FROM validation", conn)
    conn.close()
    return df

@st.cache_data
def charger_batiments_csv(fichier_csv):
    return pd.read_csv(fichier_csv)

fichier_csv = "batiments_agricoles_kepler.csv"
df = charger_batiments_csv(fichier_csv)
# Correction Arrow: conversion explicite des colonnes object en chaînes de caractères
for col in df.select_dtypes(include=['object']).columns:
    df[col] = df[col].astype(str)
# Correction Arrow: conversion explicite des float en str pour toutes les colonnes
for col in df.columns:
    if df[col].dtype == 'float64':
        df[col] = df[col].astype(str)
# Correction Arrow: conversion explicite de la colonne google_maps en str (sécurité)
df['google_maps'] = df['google_maps'].astype(str)

# --- Filtres latéraux dynamiques ---
nature = st.sidebar.multiselect('Nature', sorted(df['nature'].dropna().unique()), key='nature_filter')
etat = st.sidebar.multiselect('Etat de l\'objet', sorted(df['etat_de_l_objet'].dropna().unique()), key='etat_filter')
statuts = ["Tous", "Non évalué", "Validé", "Refusé"]
filtre_statut = st.sidebar.selectbox('Filtrer par statut d\'évaluation', statuts, key='statut_filter')

df_filtered = df.copy()
if nature:
    df_filtered = df_filtered[df_filtered['nature'].isin(nature)]
if etat:
    df_filtered = df_filtered[df_filtered['etat_de_l_objet'].isin(etat)]

# --- Chargement des validations en base ---
all_valids = select_all_validations()
# Ajout d'un filtre par statut d'évaluation

if filtre_statut != "Tous":
    if filtre_statut == "Non évalué":
        cleabs_evalues = set(all_valids['cleabs'])
        df_filtered = df_filtered[~df_filtered['cleabs'].isin(cleabs_evalues)]
    else:
        cleabs_statut = set(all_valids[all_valids['validation'] == filtre_statut]['cleabs'])
        df_filtered = df_filtered[df_filtered['cleabs'].isin(cleabs_statut)]

# --- Filtre bâtiments non évalués ---
filtre_non_evalues = st.sidebar.checkbox('Afficher uniquement les bâtiments non évalués')
if filtre_non_evalues:
    df_filtered = df_filtered[~df_filtered['cleabs'].isin(cleabs_evalues)]

# --- Navigation séquentielle ---
if 'selected_idx' not in st.session_state:
    st.session_state.selected_idx = 0
if 'nav_action' not in st.session_state:
    st.session_state.nav_action = None

# Gestion navigation AVANT affichage
try:
    rerun_func = st.rerun
except AttributeError:
    rerun_func = None

if st.session_state.nav_action == "prev" and st.session_state.selected_idx > 0:
    st.session_state.selected_idx -= 1
    st.session_state.nav_action = None
    if rerun_func:
        rerun_func()
elif st.session_state.nav_action == "next" and st.session_state.selected_idx < len(df_filtered) - 1:
    st.session_state.selected_idx += 1
    st.session_state.nav_action = None
    if rerun_func:
        rerun_func()

total = len(df_filtered)
if total == 0:
    st.warning("Aucun bâtiment trouvé.")
    st.stop()

filtered_indices = df_filtered.index.to_list()
current_pos = st.session_state.selected_idx
if current_pos >= total:
    current_pos = 0

current_index = filtered_indices[current_pos]
row = df_filtered.loc[current_index]
cleabs = row['cleabs']

# --- Lecture du statut/comm --
old_val, old_com = get_validation(cleabs)

st.markdown(f"### {current_pos+1}/{total} — Bâtiment ID {cleabs}")
st.table(row)

# --- Carte interactive (fond satellite) ---
st.write("#### Localisation")
m = folium.Map(location=[row['lat'], row['lon']], zoom_start=19, tiles=None)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='ESRI', name='Satellite'
).add_to(m)
folium.Marker([row['lat'], row['lon']], popup=f"ID : {cleabs}").add_to(m)
st_folium(m, width=700, height=400)
st.markdown(f"[Voir dans Google Maps]({row['google_maps']})", unsafe_allow_html=True)

# --- Champ commentaire (bonus) ---
new_commentaire = st.text_input("Commentaire éventuel (optionnel)", value=old_com if old_com else "")

# --- Boutons navigation + validation/refus (persistance SQLite) ---
col1, col2, col3, col4 = st.columns([1,1,2,1])
with col1:
    if st.button("⬅️ Précédent", key="prev_btn"):
        st.session_state.nav_action = "prev"
with col2:
    if st.button("➡️ Suivant", key="next_btn"):
        st.session_state.nav_action = "next"
with col3:
    v = None
    if st.button("✅ Valider"):
        set_validation(cleabs, "Validé", new_commentaire)
        v = "Validé"
    if st.button("❌ Refuser"):
        set_validation(cleabs, "Refusé", new_commentaire)
        v = "Refusé"
    # Rafraîchit status visuel
    val_display = v if v else old_val
    if val_display:
        st.success(f"Statut en base : **{val_display}**")
    else:
        st.info("Non évalué")
with col4:
    if st.button("Retour à la liste (reset)") :
        st.session_state.selected_idx = 0

# --- Export des résultats depuis SQLite ---
all_valids = select_all_validations()
res = pd.merge(df, all_valids, how="left", on="cleabs")
st.download_button(
    label="Télécharger validations globales (CSV)",
    data=res.to_csv(index=False),
    file_name="validation_batiments.sqlite.csv"
)
