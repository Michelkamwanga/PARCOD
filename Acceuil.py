import streamlit as st
from PIL import Image
import pandas as pd

# Charger le logo de l'organisation
logo_path = 'logo.png'  # Remplacez par le chemin de votre logo
logo = Image.open(logo_path)

# Titre de la page
st.set_page_config(page_title="Gestion de temps journalier - Personnel Activity Report (PAR)", layout="wide")

# Afficher le logo en haut à droite
col1, col2 = st.columns([5, 1])
with col2:
    st.image(logo, use_column_width=True)

# Grand titre
st.title("Gestion de temps journalier - PAR")

# Auteur
st.subheader("Auteur : Département de la cellule technique de CARE RDC")

# Texte de notice
st.write("""
Pour mieux remplir votre PAR, prenez les informations qui vous ont été partagées par l'équipe GRANT, 
puis allez vers le menu PAR (à gauche de votre écran), saisissez le mois et l'année concernés ainsi que le jour 
du mois de remplissage de PAR pour permettre à l'application de bien situer de quelle quinzaine s'agit-il. 
Rassurez-vous que la colonne de Pourcentage ait des valeurs au format normal (ex : au lieu de 30% mettez 30).
""")

# Option de téléchargement du fichier Excel via un lien externe
st.write("Vous pouvez télécharger un exemple de fichier ici :")
st.markdown("[Télécharger PAR FUNDING DATA.xlsx](https://careinternational-my.sharepoint.com/:x:/g/personal/michel_kamwanga_care_org/EesQLtLZq3lBnrXu8Q1JWi0Bfr0L4uYhgD3NrsAdoCMODA)")

# Calendrier des jours fériés
st.header("Calendrier des jours fériés")

# Création des données des jours fériés
jours_feries = {
    "Mois": [
        "Janvier", "Janvier", "Janvier", "Janvier",
        "Avril",
        "Mai", "Mai",
        "Juin",
        "Août", "Août", "Août", "Août",
        "Novembre",
        "Décembre", "Décembre", "Décembre", "Décembre"
    ],
    "Jours fériés": [
        "1er (Nouvel an) - 2 janvier",
        "4 (Martyrs de l'indépendance)",
        "16 (Mort de Lumumba)",
        "17 (Mort de Kabila père)",
        "10 (Lundi de Pâques)",
        "1er (Fête du Travail)",
        "17 (Anniversaire de la libération)",
        "30 (Anniversaire de l'indépendance)",
        "1er (Fête des Parents)",
        "15 (Fête de l'Assomption)",
        "Clôture du Ramadan à déterminer",
        "Fête de mouton à déterminer",
        "1er (Fête de la Toussaint)",
        "24 (Festivités de fin d'année)",
        "25 (Festivités de fin d'année)",
        "31 (Festivités de fin d'année)",
        "24 décembre prise le 22 décembre"
    ]
}

# Convertir en DataFrame
df_jours_feries = pd.DataFrame(jours_feries)

# Afficher le tableau des jours fériés
st.table(df_jours_feries)