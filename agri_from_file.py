import geopandas as gpd

# Charger le RPG Hérault (voir chemin d’accès correct)
rpg_file = 'RPG_2023_SURF_PARCELLE_S_034.shp'
rpg = gpd.read_file(rpg_file)

# Sélectionner uniquement la commune de Ganges (code INSEE 34111)
rpg_ganges = rpg[rpg['ID_COM'] == '34111']

# Optionnel : filtrer seulement certaines cultures, par ex. les « parcelles principales »
# ou exporter
rpg_ganges.to_file('GANGES_RPG_parcelles_agricoles.geojson', driver='GeoJSON')

print(f"Nombre de parcelles agricoles déclarées à la PAC à Ganges : {len(rpg_ganges)}")
print(rpg_ganges[['ILOT', 'PARCELLE', 'CODE_CULTU', 'AN_CULTU', 'SURF_PARC', 'ID_PAR']].head())
