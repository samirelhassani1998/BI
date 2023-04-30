import streamlit as st
import geopandas as gpd
import requests
from io import BytesIO
from zipfile import ZipFile

st.title("Parcelles en Agriculture Biologique déclarées à la PAC")

# Charger les données à partir de l'URL
url = "https://static.data.gouv.fr/resources/parcelles-en-agriculture-biologique-ab-declarees-a-la-pac/20221122-124454/rpg-bio-2021-national.shp.zip"
response = requests.get(url)
with ZipFile(BytesIO(response.content)) as zf:
    shp = gpd.read_file(zf.open("rpg-bio-2021-national.shp"))

# Afficher un extrait des données
st.write(shp.head())

# Afficher les données sur une carte
st.map(shp)
