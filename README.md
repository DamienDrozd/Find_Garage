# Find Garage - Analyse des Bâtiments Agricoles

## Description

Ce projet est un système d'analyse et de validation de bâtiments agricoles utilisant des données géospatiales. Il permet d'extraire, visualiser et valider manuellement des bâtiments agricoles à partir des données de la BD TOPO de l'IGN.

## Fonctionnalités

- **Extraction de données géospatiales** : Traitement des données de la BD TOPO pour identifier les bâtiments agricoles
- **Interface de validation interactive** : Application Streamlit pour visualiser et valider manuellement chaque bâtiment
- **Cartographie interactive** : Visualisation sur cartes avec fonds satellite
- **Base de données de validation** : Stockage SQLite des validations utilisateur
- **Export de données** : Export en CSV et Excel des résultats

## Structure du projet

```
.
├── agri_from_file.py          # Extraction des parcelles agricoles RPG
├── analyse_streamlit.py       # Application Streamlit de validation
├── topo_from_file.py          # Traitement des données BD TOPO
├── parcelle_api.py            # API Carto IGN pour données cadastrales
├── batiments_agricoles_kepler.csv    # Données exportées pour Kepler.gl
├── batiments_agricoles.xlsx   # Export Excel des bâtiments
├── carte_batiments_agricoles.html    # Carte HTML interactive
├── resultats_batiments.sqlite # Base de données des validations
└── BD/                        # Données BD TOPO (GeoPackage)
```

## Installation

### Prérequis

- Python 3.8+
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### 1. Traitement des données BD TOPO

```bash
python topo_from_file.py
```

Ce script :
- Charge les données de bâtiments depuis le fichier GeoPackage BD TOPO
- Filtre les bâtiments agricoles par usage et nature
- Génère les fichiers CSV, Excel et HTML de sortie

### 2. Application de validation Streamlit

```bash
streamlit run analyse_streamlit.py
```

L'application permet de :
- Visualiser chaque bâtiment agricole sur une carte satellite
- Filtrer par nature, état, et statut de validation
- Valider ou refuser chaque bâtiment avec commentaires
- Naviguer séquentiellement dans la liste des bâtiments
- Exporter les résultats de validation

### 3. Extraction des parcelles RPG

```bash
python agri_from_file.py
```

Extrait les parcelles agricoles déclarées à la PAC pour la commune de Ganges.

### 4. Requête API cadastrale

```bash
python parcelle_api.py
```

Interroge l'API Carto de l'IGN pour récupérer les données cadastrales.

## Configuration

### Fichiers de données requis

- **BD TOPO** : Placer le fichier GeoPackage dans le dossier `BD/`
- **RPG** : Fichier shapefile `RPG_2023_SURF_PARCELLE_S_034.shp` pour les données RPG

### Paramètres modifiables

Dans `topo_from_file.py` :
- `distance_km` : Distance maximale depuis Montpellier (défaut: 100km)
- Critères de filtrage des bâtiments agricoles

Dans `analyse_streamlit.py` :
- `DB_FILE` : Nom de la base de données SQLite
- `fichier_csv` : Fichier CSV source des bâtiments

## Base de données

Le projet utilise SQLite pour stocker les validations :

```sql
CREATE TABLE validation (
    cleabs TEXT PRIMARY KEY,        -- Identifiant unique du bâtiment
    validation TEXT,                -- "Validé" ou "Refusé"
    commentaire TEXT DEFAULT NULL   -- Commentaire optionnel
);
```

## Export des données

### Formats supportés
- **CSV** : Pour Kepler.gl et analyse
- **Excel** : Feuilles séparées par type de bâtiment
- **GeoJSON** : Pour les parcelles RPG
- **HTML** : Cartes interactives Folium

### Colonnes principales
- `cleabs` : Identifiant unique IGN
- `lat`, `lon` : Coordonnées géographiques
- `nature` : Type de bâtiment
- `usage_1` : Usage principal
- `etat_de_l_objet` : État du bâtiment
- `google_maps` : Lien Google Maps

## Technologies utilisées

- **GeoPandas** : Traitement des données géospatiales
- **Streamlit** : Interface web interactive
- **Folium** : Cartographie web
- **SQLite** : Base de données locale
- **Pandas** : Manipulation de données
- **Shapely** : Géométries et calculs spatiaux

## Auteur

Projet d'analyse de bâtiments agricoles - 2025

## Licence

[À définir]
