import requests
import json

# Code INSEE de Ganges
code_insee = '34111'

# URL de l'API Carto pour les bâtiments cadastraux
url_batiments = f'https://apicarto.ign.fr/api/cadastre/parcelle?code_insee={code_insee}'

# Requête GET pour récupérer les données
response = requests.get(url_batiments)

# Vérification du statut de la réponse
if response.status_code == 200:
    data = response.json()
    # Traitement des données récupérées
    for feature in data['features']:
        # Exemple : afficher les propriétés de chaque bâtiment
        print(json.dumps(feature['properties'], indent=4, ensure_ascii=False))
else:
    print(f"Erreur lors de la récupération des données : {response.status_code}")
