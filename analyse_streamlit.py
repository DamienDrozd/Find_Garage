import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
# streamlit run analyse_streamlit.py

# 

# --- Paramétrage base de données ---
# Utilise DATABASE_URL pour PostgreSQL, sinon fallback vers SQLite
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///resultats_batiments.sqlite')

# Correction pour les URLs PostgreSQL avec le dialecte 'postgres'
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def get_engine():
    """Crée et retourne un moteur SQLAlchemy"""
    return create_engine(DATABASE_URL)

def create_or_open_db():
    """Initialise la base de données et crée les tables si nécessaire"""
    engine = get_engine()
    with engine.connect() as conn:
        # Créer la table validation si elle n'existe pas
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS validation (
                cleabs TEXT PRIMARY KEY,
                validation TEXT,
                commentaire TEXT DEFAULT NULL
            )
        '''))
        conn.commit()
    return engine

def set_validation(cleabs, validation, commentaire=None):
    """Enregistre ou met à jour une validation dans la base de données"""
    engine = get_engine()
    with engine.connect() as conn:
        # Utilise UPSERT compatible PostgreSQL et SQLite
        if 'postgresql' in DATABASE_URL:
            # Syntaxe PostgreSQL
            conn.execute(text('''
                INSERT INTO validation (cleabs, validation, commentaire)
                VALUES (:cleabs, :validation, :commentaire)
                ON CONFLICT(cleabs) DO UPDATE SET 
                    validation = EXCLUDED.validation, 
                    commentaire = EXCLUDED.commentaire
            '''), {"cleabs": cleabs, "validation": validation, "commentaire": commentaire})
        else:
            # Syntaxe SQLite
            conn.execute(text('''
                INSERT INTO validation (cleabs, validation, commentaire)
                VALUES (:cleabs, :validation, :commentaire)
                ON CONFLICT(cleabs) DO UPDATE SET 
                    validation = excluded.validation, 
                    commentaire = excluded.commentaire
            '''), {"cleabs": cleabs, "validation": validation, "commentaire": commentaire})
        conn.commit()

def get_validation(cleabs):
    """Récupère la validation et le commentaire pour un cleabs donné"""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text('SELECT validation, commentaire FROM validation WHERE cleabs = :cleabs'), 
            {"cleabs": cleabs}
        )
        row = result.fetchone()
        return (row[0], row[1]) if row else (None, None)

def select_all_validations():
    """Récupère toutes les validations depuis la base de données"""
    engine = get_engine()
    df = pd.read_sql_query("SELECT * FROM validation", engine)
    return df

@st.cache_data
def charger_batiments_csv(fichier_csv):
    return pd.read_csv(fichier_csv)

# --- Initialisation de la base de données ---
create_or_open_db()

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
