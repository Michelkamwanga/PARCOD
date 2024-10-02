import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Chargement du fichier Excel
def load_data(file):
    df = pd.read_excel(file)
    return df

# Fonction pour obtenir les jours fériés d'une période donnée
def get_holidays(start_date, end_date):
    holidays = {
        datetime(start_date.year, 1, 1): "Nouvel an",
        datetime(start_date.year, 1, 2): "Jour après le Nouvel an",
        datetime(start_date.year, 1, 4): "Martyrs de l'indépendance",
        datetime(start_date.year, 1, 16): "Mort de Lumumba",
        datetime(start_date.year, 1, 17): "Mort de Kabila père",
        datetime(start_date.year, 4, 10): "Lundi de Pâques",
        datetime(start_date.year, 5, 1): "Fête du Travail",
        datetime(start_date.year, 5, 17): "Anniversaire de la libération",
        datetime(start_date.year, 6, 30): "Anniversaire de l'indépendance",
        datetime(start_date.year, 8, 1): "Fête des Parents",
        datetime(start_date.year, 8, 15): "Fête de l'assomption",
        datetime(start_date.year, 11, 1): "Fête de la Toussaint",
        datetime(start_date.year, 12, 25): "Noël",
    }

    holidays_in_period = {date: name for date, name in holidays.items() if start_date <= date <= end_date}
    return holidays_in_period

# Fonction pour calculer les heures de travail
def calculate_hours(df, start_date, end_date):
    # Inclure tous les jours (y compris les week-ends)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    hours_table = pd.DataFrame(index=df['FC Name'], columns=[f"{date.strftime('%A %d-%m')}" for date in date_range])
    
    total_work_hours_per_day = 8
    num_working_days = len(date_range[date_range.weekday < 5])  # Nombre de jours de semaine
    total_hours = total_work_hours_per_day * num_working_days

    for i, row in df.iterrows():
        pourcentage = row['Pourcentage'] / 100
        project_hours = pourcentage * total_hours
        daily_hours = project_hours / num_working_days if num_working_days > 0 else 0

        for day in date_range:
            if day in pd.date_range(start=start_date, end=end_date, freq='B'):  # Vérifier si c'est un jour de travail
                hours_table.loc[row['FC Name'], day.strftime('%A %d-%m')] = round(daily_hours, 1)

    # Remplir les week-ends avec NaN
    for day in date_range:
        if day.strftime('%A %d-%m') not in hours_table.columns:
            hours_table[day.strftime('%A %d-%m')] = np.nan

    hours_table.loc['Total'] = hours_table.sum()

    return hours_table, total_hours

# Fonction pour exporter les heures calculées en Excel
def export_to_excel(hours_table):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        hours_table.fillna('', inplace=True)
        hours_table.to_excel(writer, sheet_name='Heures', index=True)
        
        workbook = writer.book
        worksheet = writer.sheets['Heures']

        header_format = workbook.add_format({'bold': True, 'font_color': 'red', 'bg_color': '#4F81BD'})
        cell_format = workbook.add_format({'border': 1})

        worksheet.set_row(0, None, header_format)
        for col_num in range(hours_table.shape[1]):
            worksheet.write(0, col_num, hours_table.columns[col_num], header_format)
        
        for row_num in range(1, hours_table.shape[0] + 1):
            for col_num in range(hours_table.shape[1]):
                worksheet.write(row_num, col_num, hours_table.iat[row_num - 1, col_num], cell_format)

    output.seek(0)
    return output

# Fonction pour générer un graphique général des heures par projet
def plot_hours_general(hours_table):
    # Supprimer la ligne 'Total' si elle est présente dans le tableau
    hours_table_no_total = hours_table.drop('Total', errors='ignore')

    # Calculer le total des heures pour chaque projet (somme sur toutes les colonnes de date)
    total_hours_per_project = hours_table_no_total.sum(axis=1).reset_index()
    total_hours_per_project.columns = ['Projet', 'Total Heures']

    # Créer un graphique avec Plotly montrant les heures totales par projet
    fig = px.bar(total_hours_per_project, x='Projet', y='Total Heures',
                 title='Heures totales par Projet', labels={'Total Heures': 'Heures Totales'},
                 text_auto=True)

    fig.update_layout(xaxis_title='Projet', yaxis_title='Heures Totales', legend_title='Projets')
    return fig

# Fonction pour exporter les heures en JPG avec une meilleure lisibilité
def export_to_jpg(hours_table):
    fig, ax = plt.subplots(figsize=(20, 10))  # Augmenter la taille de la figure
    ax.axis('tight')
    ax.axis('off')

    # Créer le tableau avec une taille de police ajustée
    table = ax.table(cellText=hours_table.values, colLabels=hours_table.columns, rowLabels=hours_table.index, loc='center', cellLoc='center')

    # Ajuster la taille de la police
    table.auto_set_font_size(False)
    table.set_fontsize(12)  # Taille de la police augmentée
    table.scale(1.2, 1.2)   # Agrandir les cellules du tableau

    # Sauvegarder l'image en format JPG
    output = io.BytesIO()
    FigureCanvas(fig).print_jpg(output)
    output.seek(0)
    return output

# Interface utilisateur avec Streamlit
def main():
    st.markdown("<h1 style='color: orange;'>Gestion de Temps de Travail - PAR</h1>", unsafe_allow_html=True)

    # Saisie du mois, de l'année et du jour
    col1, col2, col3 = st.columns(3)
    with col1:
        mois = st.number_input("Mois", min_value=1, max_value=12, step=1)
    with col2:
        annee = st.number_input("Année", min_value=2000, max_value=2100, step=1)
    with col3:
        jour = st.number_input("Jour", min_value=1, max_value=31, step=1)

    # Téléchargement du fichier Excel
    uploaded_file = st.file_uploader("Télécharger le fichier Excel", type=["xlsx"])
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        # Affichage ou masquer les données
        show_data = st.checkbox("Afficher les données importées")
        
        if show_data:
            st.write("Données importées :", df)

        # Classification de la quinzaine
        if jour <= 15:
            start_date = datetime(annee, mois, 1)
            end_date = datetime(annee, mois, 15)
        else:
            start_date = datetime(annee, mois, 16)
            end_date = datetime(annee, mois, (30 if mois in [4, 6, 9, 11] else (29 if mois == 2 and annee % 4 == 0 else 28) if mois == 2 else 31))

        # Calcul et affichage du tableau des heures
        hours_table, total_hours = calculate_hours(df, start_date, end_date)
        st.write("Tableau des heures calculées :")
        st.dataframe(hours_table)

        # Affichage des jours fériés dans la période
        holidays_in_period = get_holidays(start_date, end_date)
        if holidays_in_period:
            st.write("Jours fériés dans la période :")
            for date, name in holidays_in_period.items():
                st.write(f"{date.strftime('%d-%m-%Y')}: {name}")
        else:
            st.write("Aucun jour férié dans la période.")

        # Affichage du total général des heures
        st.write(f"Total général des heures sur la période : {total_hours}")

        # Affichage du graphique des heures totales par projet avec étiquettes de données
        st.plotly_chart(plot_hours_general(hours_table))

        # Boutons pour exporter les données en Excel et en JPG
        col_export_excel, col_export_jpg = st.columns(2)
        with col_export_excel:
            if st.button("Exporter en Excel"):
                excel_data = export_to_excel(hours_table)
                st.download_button(label="Télécharger le fichier Excel", data=excel_data, file_name="heures_calculees.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        with col_export_jpg:
            if st.button("Exporter le tableau PAR en JPG/Photo"):
                jpg_data = export_to_jpg(hours_table)
                st.download_button(label="Télécharger le fichier JPG", data=jpg_data, file_name="heures_calculees.jpg", mime="image/jpeg")

if __name__ == '__main__':
    main()