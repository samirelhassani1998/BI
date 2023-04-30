import streamlit as st
import geopandas as gpd
import requests
from io import BytesIO
from zipfile import ZipFile
import tempfile
import os

st.title("Parcelles en Agriculture Biologique déclarées à la PAC")

# Charger les données à partir de l'URL
url = "https://static.data.gouv.fr/resources/parcelles-en-agriculture-biologique-ab-declarees-a-la-pac/20221122-124454/rpg-bio-2021-national.shp.zip"
response = requests.get(url)

with tempfile.TemporaryDirectory() as tmpdirname:
    with ZipFile(BytesIO(response.content)) as zf:
        zf.extractall(tmpdirname)
    
    shp_path = [os.path.join(tmpdirname, file) for file in os.listdir(tmpdirname) if file.endswith(".shp")][0]
    shp = gpd.read_file(shp_path)

# Afficher un extrait des données
st.write(shp.head())

# Afficher les données sur une carte
st.map(shp)
