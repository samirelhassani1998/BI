import pandas as pd
import numpy as np
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
from PIL import Image

# Chemin d'accès à votre photo de profil
photo_profil = r"C:\Users\Samir\Downloads\profile-pic.png"

# Afficher la photo de profil dans la barre latérale
image = Image.open(photo_profil)
st.sidebar.image(image, use_column_width=True)

# Informations personnelles
nom = "El Hassani"
prenom = "Samir"
linkedin = "https://www.linkedin.com/in/elhassanisamir/"
github = "https://github.com/samirelhassani1998"

# Afficher les informations dans la barre latérale
st.sidebar.title("Informations personnelles")
st.sidebar.subheader("Nom")
st.sidebar.text(nom)
st.sidebar.subheader("Prénom")
st.sidebar.text(prenom)
st.sidebar.subheader("LinkedIn")
st.sidebar.markdown(f'<a href="{linkedin}" target="_blank"><img src="https://blog.waalaxy.com/wp-content/uploads/2021/01/index.png" alt="LinkedIn" width="150"></a>', unsafe_allow_html=True)
st.sidebar.subheader("GitHub")
st.sidebar.markdown(f'<a href="{github}" target="_blank"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub" width="150"></a>', unsafe_allow_html=True)
selected_year = st.selectbox("Choose a year to analyze", list(range(1972, 2023)))

def download_unzip(zipurl, destination):
    """Télécharger le fichier zip depuis l'URL et l'extraire vers la destination"""
    with urlopen(zipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(destination)

# Année pour laquelle vous souhaitez télécharger les données
year_to_download = selected_year

# Vérifier si le fichier est déjà téléchargé
data_path = "C:/Users/Samir/Downloads/dataset"  # Chemin vers le répertoire de téléchargement
csv_file_path = os.path.join(data_path, f"Deces_{year_to_download}.csv")

if os.path.exists(csv_file_path):
    print(f"Le fichier pour l'année {year_to_download} existe déjà dans le chemin spécifié.")
else:
    # Télécharger et extraire les fichiers CSV depuis les URL
    if 1970 <= year_to_download <= 2019:
        decade = year_to_download // 10 * 10
        url = f"https://www.insee.fr/fr/statistiques/fichier/4769950/deces-{decade}-{decade + 9}-csv.zip"
        print("Téléchargement et extraction de", url)
        download_unzip(url, data_path)
    elif 2020 <= year_to_download <= 2023:
        url = f"https://www.insee.fr/fr/statistiques/fichier/4190491/Deces_{year_to_download}.zip"
        print("Téléchargement et extraction de", url)
        download_unzip(url, data_path)

# Charger les données dans un DataFrame
csv_file_path = os.path.join(data_path, f"Deces_{year_to_download}.csv")

if os.path.exists(csv_file_path):
    # Ici, j'ajoute 'paysnaiss' à la liste des colonnes utilisées
    df = pd.read_csv(csv_file_path, sep=';', usecols=['datenaiss', 'datedeces', 'sexe', 'paysnaiss'],
                     parse_dates=['datenaiss', 'datedeces'])
else:
    print("Le fichier CSV pour l'année sélectionnée n'a pas été trouvé.")
    df = pd.DataFrame()


# Remplacer les chaînes de caractères vides par des valeurs NaN
df.replace('', np.nan, inplace=True)

def parse_dates(date):
    try:
        return pd.to_datetime(date, format='%Y%m%d')
    except ValueError:
        return pd.NaT

df['datenaiss'] = df['datenaiss'].apply(parse_dates)
df['datedeces'] = df['datedeces'].apply(parse_dates)



# Calculer l'âge en années
df['age'] = (df['datedeces'] - df['datenaiss']) / np.timedelta64(1, 'Y')


# Filtrer les années selon l'année sélectionnée
df = df[df['age'] >= 0]
df = df[df['datedeces'].dt.year == year_to_download]

# Extraction de l'année et du mois de la date de décès
df['death_year'] = df['datedeces'].dt.year
df['death_month'] = df['datedeces'].dt.month

# Filtration des données pour l'année sélectionnée
df_selected_year = df[df['death_year'] == selected_year]

# Create women and men dataframes
women = df_selected_year[df_selected_year['sexe'] == 2]
men = df_selected_year[df_selected_year['sexe'] == 1]

# Grouper par mois
by_month = df_selected_year.groupby('death_month').size()
by_month_women = df_selected_year[df_selected_year['sexe'] == 2].groupby('death_month').size()
by_month_men = df_selected_year[df_selected_year['sexe'] == 1].groupby('death_month').size()

# Création du graphique
fig, ax = plt.subplots()
by_month.plot(label="Total", ax=ax)
by_month_women.plot(style='--', ax=ax, label="Women")
by_month_men.plot(style='-.', ax=ax, label="Men")
ax.set_ybound(lower=0)
ax.set_xlabel("Month")
ax.set_title(f"Number of deaths in {selected_year}")
ax.legend()

# Afficher le graphique dans Streamlit
st.pyplot(fig)

def get_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Return sub dataframe corresponding to decease year"""
    return df[df['datedeces'].dt.year == year]

BINS = 100  # Définissez BINS selon le nombre de bins que vous voulez pour votre histogramme

ANNOTATIONS = {}  # Vous devez définir ANNOTATIONS selon les annotations que vous voulez sur le graphique

sns.set()  # Utilisez Seaborn pour améliorer l'esthétique du graphique

def plot_year(df: pd.DataFrame, year: int, annotate=False):
    """Plot one year histogram and return fig, ax"""
    fig, ax = plt.subplots()
    ax.set_xlabel('Age of death (years)', fontsize=14)
    ax.hist(get_year(df, year)['age'],
            BINS,
            range=[0, BINS],
            color='skyblue',  # Utilisez une couleur plus agréable
            edgecolor='black')  # Ajoutez des bords aux barres pour une meilleure distinction
    fig.suptitle("Distribution of the age of death in France", fontsize=16)
    ax.set_title(f"Year of death: {year}", fontsize=16)
    ax.set_xlim([0, BINS])
    ax.set_ylim([0, 27500])
    ax.set_ylabel("Number of deaths", fontsize=14)
    ax.grid(True)  # Ajoutez une grille pour une meilleure lisibilité
    if annotate:
        for birthyear, text in ANNOTATIONS.items():
            age = year - birthyear
            vl = ax.axvline(age - 1, color='r', linewidth=0.75)
            text = ax.text(age - 10, 23000, text, color='r',
                           bbox=dict(facecolor='white', alpha=0.75))
    plt.show()  # Affichez le graphique avec plt.show() pour une meilleure intégration avec Seaborn
    return fig, ax
fig, ax = plot_year(df, selected_year, annotate=True)
st.pyplot(fig)

def plot_year_wm(women, men, year: int):
    """Plot one year histogram and return fig"""
    # Utiliser les données de l'année sélectionnée
    df_selected_year = df[df['death_year'] == year]
    women = df_selected_year[df_selected_year['sexe'] == 2]
    men = df_selected_year[df_selected_year['sexe'] == 1]

    # Initialize figure
    fig, axes = plt.subplots(ncols=2, sharey=True)
    fig.suptitle(f"Distribution of the age of death in France in {year} by sex")

    # Graphique pour les femmes
    axes[0].set_ylabel("Age of death (years)")
    axes[0].hist(women['age'], BINS, range=[0, BINS], color='skyblue', edgecolor='black')
    axes[0].invert_xaxis()
    axes[0].set_title("Number of deaths of women")  # Ajout du titre

    # Graphique pour les hommes
    axes[1].hist(men['age'], BINS, range=[0, BINS], color='skyblue', edgecolor='black')
    axes[1].set_title("Number of deaths of men")  # Ajout du titre

    fig.tight_layout()
    return fig


fig = plot_year_wm(women, men, selected_year)

# Afficher le graphique dans Streamlit
st.pyplot(fig)

# Obtenez les 10 pays de naissance les plus fréquents
top10_countries = df['paysnaiss'].value_counts().nlargest(10)

# Créez le graphique
fig, ax = plt.subplots()
sns.barplot(x=top10_countries.index, y=top10_countries.values, ax=ax)
plt.xticks(rotation=90)  # Faites pivoter les étiquettes de l'axe x pour qu'elles soient lisibles
ax.set_title("Top 10 countries of birth")
ax.set_xlabel("Country of birth")
ax.set_ylabel("Number of deaths")

# Affichez le graphique dans Streamlit
st.pyplot(fig)

# Diviser les âges en tranches
age_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, np.inf]
age_labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100', '100+']

# Appliquer la découpe en tranches d'âge au DataFrame
df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)

# Compter le nombre de décès dans chaque tranche d'âge
age_group_counts = df['age_group'].value_counts().sort_index()

# Créer le graphique
fig, ax = plt.subplots()
age_group_counts.plot(kind='bar', ax=ax)
ax.set_xlabel('Age Group')
ax.set_ylabel('Number of Deaths')
ax.set_title('Distribution of Deaths by Age Group')
plt.xticks(rotation=45)

# Afficher le graphique dans Streamlit
st.pyplot(fig)

import plotly.graph_objects as go

# Create a new figure
fig = go.Figure()

# Add traces for total, women, and men
fig.add_trace(go.Scatter(x=by_month.index, y=by_month.values,
                    mode='lines',
                    name='Total'))
fig.add_trace(go.Scatter(x=by_month_women.index, y=by_month_women.values,
                    mode='lines+markers',
                    name='Women'))
fig.add_trace(go.Scatter(x=by_month_men.index, y=by_month_men.values,
                    mode='lines',
                    name='Men'))

# Update layout
fig.update_layout(title=f"Number of deaths in {selected_year}",
                   xaxis_title="Month",
                   yaxis_title="Number of deaths",
                   legend_title="Sex")

# Display the figure in Streamlit
st.plotly_chart(fig)
