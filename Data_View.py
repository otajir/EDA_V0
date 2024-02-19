import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Définir le titre de l'application
st.title("Explorateur de Données")

# Chargement du fichier
@st.cache(allow_output_mutation=True)
def load_data(file):
    if file:
        if file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':  # Excel file
            xl = pd.ExcelFile(file)
            return xl
        elif file.type == 'text/csv':  # CSV file
            return pd.read_csv(file)

# Ajouter une zone d'upload pour les fichiers XLSX et CSV
uploaded_file = st.file_uploader("Uploader un fichier (CSV ou XLSX)", type=["csv", "xlsx"])

# Afficher les données après le chargement
if uploaded_file is not None:
    data = load_data(uploaded_file)

    if isinstance(data, pd.ExcelFile):  # If Excel file with multiple sheets
        sheet_name = st.selectbox("Sélectionner la feuille à explorer", data.sheet_names)
        df = data.parse(sheet_name)
    else:  # If CSV file
        df = data

    # Afficher les premières lignes du DataFrame
    st.subheader("Explorer les données")
    st.write("Les premières lignes du DataFrame : ")
    st.write(df.head())
    
    # Afficher des statistiques sommaires
    st.subheader("Statistiques sommaires")
    st.write("Statistiques sommaires : ")
    st.write(df.describe())

    # Stocker la dataframe dans la session pour la visualisation
    st.session_state.df = df

# Visualisation des données
if 'df' in st.session_state:
    df_visualize = st.session_state.df

    # Afficher la page de visualisation
    st.subheader("Visualisation des données")

    # Sélection du type de graphique
    chart_type = st.selectbox("Sélectionner le type de graphique", ["Ligne", "Barres", "Histogramme", "Diagramme circulaire"])

    if chart_type == "Ligne":
        # Créer le graphique avec Plotly Graph Objects
        fig = go.Figure()

        # Sélection de la colonne pour l'axe X
        x_column = st.selectbox("Sélectionner la colonne pour l'axe X", df_visualize.columns)

        # Sélection des colonnes à visualiser pour l'axe Y
        y_columns = st.multiselect("Sélectionner les colonnes à visualiser pour l'axe Y", df_visualize.columns)
        
        # Styles de lignes disponibles
        line_styles = ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']

        if y_columns:
            for column in y_columns:
                # Couleur pour la colonne
                color = st.color_picker(f"Sélectionner la couleur pour {column}", "#000000")
                line_style = st.selectbox(f"Style de ligne pour {column}", line_styles)

                if st.checkbox(f"Utiliser log({column}) pour l'axe Y"):
                    fig.add_trace(go.Scatter(x=df_visualize[x_column], y=np.log(df_visualize[column]), mode='lines',
                                            name=f"log({column})", line=dict(color=color, dash=line_style)))
                else:
                    fig.add_trace(go.Scatter(x=df_visualize[x_column], y=df_visualize[column], mode='lines',
                                            name=column, line=dict(color=color, dash=line_style)))

            # Définir les coordonnées du cadre de la figure
            fig.update_layout(
                shapes=[
                    dict(
                        type="rect",
                        xref="paper",
                        yref="paper",
                        x0=0,
                        y0=0,
                        x1=1,
                        y1=1,
                        line=dict(color="black", width=1),
                        fillcolor="rgba(0,0,0,0)",
                        
                    )
                ]
            )

            # Supprimer la droite y=0
            fig.update_yaxes(zeroline=False)

            # Personnalisation du layout du graphique avec des contrôles interactifs
            st.sidebar.subheader("Options de Layout")
            graph_title = st.sidebar.text_input("Titre du Graphique", "Graphique en ligne")
            x_axis_title = st.sidebar.text_input("Titre de l'Axe X", "Axe X")
            y_axis_title = st.sidebar.text_input("Titre de l'Axe Y", "Axe Y")
            show_grid = st.sidebar.checkbox("Afficher la Grille", value=True)
            if show_grid:
                grid_color = st.sidebar.color_picker("Couleur de la Grille", "#CCCCCC")
            bg_color = st.sidebar.color_picker("Couleur de Fond", "#FFFFFF")

            # Option pour afficher ou masquer la légende
            show_legend = st.sidebar.checkbox("Afficher la Légende", value=True)

            # Options d'échelle pour l'axe X
            scale_options = {
                "Échelle par défaut": None,
                "Pas de 25": [-50, -25, 0, 25, 50, 75,100,125, 150, 175, 200],
                "Pas de 10": [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100,110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
            }
            # Contrôle interactif pour choisir l'échelle sur l'axe X
            selected_scale = st.selectbox("Choisir l'échelle sur l'axe X", list(scale_options.keys()))
            # Obtenir les valeurs d'échelle sélectionnées
            tick_values_x = scale_options[selected_scale]
            # Mise à jour de la mise en page du graphique en fonction de l'échelle sélectionnée
            xaxis_config = dict(
                showgrid=True,
                gridcolor= grid_color if show_grid else None,
            )
            if tick_values_x:
                xaxis_config['tickvals'] = tick_values_x
                xaxis_config['tickmode'] = 'array'
            else:
                xaxis_config['tickmode'] = 'auto'

            fig.update_layout(
                xaxis=xaxis_config,
                yaxis=dict(
                    showgrid=True,
                    gridcolor= grid_color if show_grid else None,
                ),
                title=graph_title,
                xaxis_title=x_axis_title,
                yaxis_title=y_axis_title,
                # xaxis=dict(showgrid=show_grid, gridcolor=grid_color if show_grid else None),
                # yaxis=dict(showgrid=show_grid, gridcolor=grid_color if show_grid else None),
                plot_bgcolor=bg_color,  # Couleur de fond du graphique
                autosize=False,  # Désactiver l'autosize pour spécifier les dimensions
                width=500,  # Largeur du graphique
                height=500,  # Hauteur du graphique
                margin=dict(l=40, r=40, t=40, b=40),  # Marge du graphique
                paper_bgcolor=bg_color,  # Couleur de fond du papier
                showlegend=show_legend  # Afficher ou masquer la légende
            )
            # Afficher le graphique
            st.plotly_chart(fig, use_container_width=True)
