import geopandas as gpd
import pandas as pd
import folium
from shapely.geometry import Point

fichier_gpkg = "BD/BDTOPO_3-4_TOUSTHEMES_GPKG_LAMB93_D034_2025-03-15/BDTOPO/1_DONNEES_LIVRAISON_2025-03-00293/BDT_3-4_GPKG_LAMB93_D034_ED2025-03-15/BDT_3-4_GPKG_LAMB93_D034-ED2025-03-15.gpkg"

def charger_batiments(fichier_gpkg):
    batiments = gpd.read_file(fichier_gpkg, layer="batiment")
    batiments = batiments.to_crs(4326)
    def get_centroid(g):
        p = g.centroid
        return p.y, p.x
    batiments['lat'], batiments['lon'] = zip(*batiments['geometry'].map(get_centroid))
    batiments['google_maps'] = batiments.apply(
        lambda r: f"https://www.google.com/maps?q={r.lat},{r.lon}", axis=1
    )
    return batiments

def filtrer_batiments(batiments):
    bat_agri_usage = batiments[batiments['usage_1'] == "Agricole"]
    bat_agri_nature = batiments[
        batiments['nature'].str.contains("agricole", case=False, na=False) |
        batiments['nature'].isin(["Serre", "Silo"])
    ]
    abandon = batiments[
        batiments['etat_de_l_objet'].isin(['Désaffecté', 'En ruine', 'Détruit', 'Inconnu'])
        | ((batiments['usage_1'] == "Agricole") & (batiments['nombre_de_logements'] == 0))
    ]
    return bat_agri_usage, bat_agri_nature, abandon

def exporter_excel(bat_agri_usage, bat_agri_nature, abandon, nom_fichier="batiments_agricoles.xlsx"):
    bat_agri_usage_df = pd.DataFrame(bat_agri_usage.drop(columns="geometry"))
    bat_agri_nature_df = pd.DataFrame(bat_agri_nature.drop(columns="geometry"))
    abandon_df = pd.DataFrame(abandon.drop(columns="geometry"))
    with pd.ExcelWriter(nom_fichier) as writer:
        bat_agri_usage_df.to_excel(writer, sheet_name="strict_usage_agricole", index=False)
        bat_agri_nature_df.to_excel(writer, sheet_name="nature_agricole", index=False)
        abandon_df.to_excel(writer, sheet_name="abandon", index=False)

def generer_carte(bat_agri_usage, nom_fichier_html='carte_batiments_agricoles.html'):
    center = [bat_agri_usage.geometry.centroid.y.mean(), bat_agri_usage.geometry.centroid.x.mean()]
    m = folium.Map(location=center, zoom_start=12)
    for idx, row in bat_agri_usage.iterrows():
        lat = row.geometry.centroid.y
        lon = row.geometry.centroid.x
        # Utilise 'cleabs' comme identifiant unique
        identifiant = row.get('cleabs', 'N/A')
        popup = f"ID: {identifiant}<br>Nature: {row.get('nature', '')}"
        folium.Marker([lat, lon], popup=popup).add_to(m)
    m.save(nom_fichier_html)
    print(f"Carte générée : {nom_fichier_html}")

def filtrer_distance_montpellier(batiments, distance_km=100):
    # Coordonnées de Montpellier (WGS84)
    lat_mtp, lon_mtp = 43.61825180053711, 3.8813648223876953
    point_mtp = Point(lon_mtp, lat_mtp)
    # Calcul de la distance en mètres (projection EPSG:3857 pour la distance)
    bat_proj = batiments.to_crs(3857)
    point_mtp_proj = Point(
        gpd.GeoSeries([point_mtp], crs=4326).to_crs(3857).x[0],
        gpd.GeoSeries([point_mtp], crs=4326).to_crs(3857).y[0]
    )
    bat_proj['distance_mtp_m'] = bat_proj.geometry.centroid.distance(point_mtp_proj)
    # Filtre à moins de 100 km
    bat_proche = bat_proj[bat_proj['distance_mtp_m'] <= distance_km * 1000]
    # On récupère les index pour filtrer l'original (WGS84)
    return batiments.loc[bat_proche.index]

def exporter_pour_kepler(batiments, nom_fichier='batiments_agricoles_kepler.csv'):
    # Ne conserver que les colonnes utiles pour Kepler ! (lat/lon, id, nature, etc)
    colonnes = ['cleabs', 'lat', 'lon', 'google_maps', 'usage_1', 'nature', 'etat_de_l_objet']
    batiments[colonnes].to_csv(nom_fichier, index=False)

# dans ton main, rajoute :

def main():
    batiments = charger_batiments(fichier_gpkg)
    batiments = filtrer_distance_montpellier(batiments, distance_km=100)
    bat_agri_usage, bat_agri_nature, abandon = filtrer_batiments(batiments)
    # exporter_excel(bat_agri_usage, bat_agri_nature, abandon)
    # generer_carte(bat_agri_usage)
    # exporter_pour_kepler(bat_agri_usage)

if __name__ == "__main__":
    main()