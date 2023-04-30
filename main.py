import streamlit as st
import geopandas as gpd
import requests
from io import BytesIO
from zipfile import ZipFile
import tempfile
import os
import folium
from streamlit_folium import folium_static

st.title("Parcelles en Agriculture Biologique déclarées à la PAC")

# Charger les données à partir de l'URL
url = "https://static.data.gouv.fr/resources/parcelles-en-agriculture-biologique-ab-declarees-a-la-pac/20221122-124454/rpg-bio-2021-national.shp.zip"

# Ajouter un indicateur de progression
progress_bar = st.progress(0)
progress_text = st.empty()

progress_text.text("Téléchargement des données...")
response = requests.get(url)
progress_bar.progress(25)

with tempfile.TemporaryDirectory() as tmpdirname:
    progress_text.text("Extraction des fichiers...")
    with ZipFile(BytesIO(response.content)) as zf:
        zf.extractall(tmpdirname)
    progress_bar.progress(50)

    progress_text.text("Chargement du fichier shapefile...")
    shp_path = [os.path.join(tmpdirname, file) for file in os.listdir(tmpdirname) if file.endswith(".shp")][0]
    shp = gpd.read_file(shp_path)
    progress_bar.progress(100)

# Supprimer l'indicateur de progression une fois les données chargées
progress_bar.empty()
progress_text.empty()

# Afficher un extrait des données
st.write(shp.head())

# Afficher les données sur une carte
m = folium.Map(location=[47.0833, 2.4000], zoom_start=6)
shp_json = shp.to_crs(epsg=4326).to_json()

folium.GeoJson(shp_json).add_to(m)
folium_static(m)
