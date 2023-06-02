import streamlit as st
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import pandas as pd
import numpy as np
import glob
from urllib.error import HTTPError
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit import plotly_chart
import plotly.express as px

@st.cache(show_spinner=False)
def download_unzip(zipurl, destination):
    """Download zipfile from URL and extract it to destination"""
    try:
        with urlopen(zipurl) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall(destination)
    except HTTPError as e:
        st.error(f"HTTP Error: {e.code} {e.reason} for URL: {zipurl}")

@st.cache(ttl=3600, show_spinner=False)  # Cache for 1 hour
def load_and_process_data(year):
    csv_files = sorted(glob.glob(f'data/*{year}*.csv'))
    n_files = len(csv_files)
    df_years = []
    for i, csv_file in enumerate(csv_files):
        df_year = pd.read_csv(csv_file,
                              sep=';',
                              usecols=[1, 2, 6],
                              parse_dates=['datenaiss', 'datedeces'],
                              infer_datetime_format=True,
                              date_parser=lambda x: pd.to_datetime(
                                  x, errors='coerce'),
                              na_filter=False)
        df_years.append(df_year)
    df = pd.concat(df_years, axis=0, ignore_index=True)

    # process data
    df = df.copy()  # make a copy before modifying
    df = df.dropna(axis='index')  
    df['age'] = (df['datedeces'] - df['datenaiss']) / np.timedelta64(1, 'Y')
    df = df[df['age'] >= 0]
    df['death_year'] = df['datedeces'].dt.year
    return df

def plot_demographic_analysis(df):
    st.header("Analyse démographique des décès")
    demographic_feature = st.selectbox("Choisissez une caractéristique démographique", ["sexe", "age", "lieu_naissance", "lieu_deces"])
    fig = px.histogram(df, x=demographic_feature)
    st.plotly_chart(fig)

def plot_temporal_analysis(df):
    st.header("Analyse temporelle des décès")
    df['death_month'] = df['datedeces'].dt.month
    df['death_year'] = df['datedeces'].dt.year
    temporal_feature = st.selectbox("Choisissez une caractéristique temporelle", ["death_month", "death_year"])
    fig = px.histogram(df, x=temporal_feature)
    st.plotly_chart(fig)

def plot_migration_analysis(df):
    st.header("Analyse des décès par lieu de naissance et lieu de décès")
    if "Code du lieu de naissance" in df.columns:
        birth_place = st.selectbox("Choisissez un lieu de naissance", df["Code du lieu de naissance"].unique())
        death_place_df = df[df["Code du lieu de naissance"] == birth_place]
        fig = px.histogram(death_place_df, x="Code du lieu de décès")
        st.plotly_chart(fig)
    else:
        st.write("La colonne 'Code du lieu de naissance' n'existe pas dans le DataFrame.")

def main():
    st.title("Visualisation des données de décès")

    st.sidebar.header("Paramètres")
    year = st.sidebar.selectbox("Choisissez une année", list(range(1970, 2024)))

    st.header("Téléchargement des données")

    if year <= 2010:
        decade = (year // 10) * 10
        zipurl = f'https://www.insee.fr/fr/statistiques/fichier/4769950/etatcivil{decade}{year % 10}.zip'
    else:
        zipurl = f'https://www.insee.fr/fr/statistiques/fichier/4769950/etatcivil{year}.zip'
    
    with st.spinner("Téléchargement et décompression des données..."):
        download_unzip(zipurl, 'data')

    st.header("Chargement et traitement des données")
    with st.spinner(f"Chargement et traitement des fichiers CSV pour l'année {year}"):
        df = load_and_process_data(year)

    plot_demographic_analysis(df)
    plot_temporal_analysis(df)
    plot_migration_analysis(df)

if __name__ == "__main__":
    main()
