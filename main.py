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

def download_unzip(zipurl, destination):
    """Download zipfile from URL and extract it to destination"""
    try:
        with urlopen(zipurl) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall(destination)
    except HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason} for URL: {zipurl}")

def load_data():
    csv_files = sorted(glob.glob('data/*.csv'))
    n_files = len(csv_files)
    df_years = []
    for i, csv_file in enumerate(csv_files):
        st.write(f"Loading {csv_file} ({i + 1}/{n_files})", end='\r', flush=True)
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
    del df_years  # free memory
    return df

def main():
    st.title("Dataviz sur Streamlit")

    st.header("Téléchargement et extraction des fichiers de données")
    for decade in 1970, 1980, 1990, 2000, 2010:
        url = f"https://www.insee.fr/fr/statistiques/fichier/4769950/deces-{decade}-{decade + 9}-csv.zip"
        st.write("Downloading and extracting", url)
        download_unzip(url, 'data')

    for year in 2020, 2023:
        url = f"https://www.insee.fr/fr/statistiques/fichier/4190491/Deces_{year}.zip"
        st.write("Downloading and extracting", url)
        download_unzip(url, 'data')

    st.success("Téléchargement et extraction des fichiers de données terminés.")

    st.header("Chargement des données")
    df = load_data()

    st.subheader("Nettoyage des données")
    df.dropna(axis='index', inplace=True)
    df['age'] = (df['datedeces'] - df['datenaiss']) / np.timedelta64(1, 'Y')
    df = df[df['age'] >= 0]

    df['death_year'] = df['datedeces'].dt.year
    women = df[df.sexe == 2]  # a subset containing women
    men = df[df.sexe == 1]  # a subset containing men

    st.subheader("Affichage des données")
    st.dataframe(df.head())

    st.subheader("Statistiques")
    template_line = "{:<10} {:,}"
    st.write(template_line.format('df', len(df)))
    st.write(template_line.format('women', len(women)))
    st.write(template_line.format('men', len(men)))

    st.subheader("Graphique des décès par année")
    sns.set()
    by_year = df.groupby('death_year').size()
    by_year_women = women.groupby('death_year').size()
    by_year_men = men.groupby('death_year').size()
    ax = by_year.plot(label="Total")
    by_year_women.plot(style='--', ax=ax, label="Women")
    by_year_men.plot(style='-.', ax=ax, label="Men")
    ax.set_ybound(lower=0)
    ax.set_xlabel("Year")
    ax.set_title("Number of deaths")
    ax.legend()

    st.pyplot(plt)

    st.success("Chargement des données terminé.")

if __name__ == "__main__":
    main()
