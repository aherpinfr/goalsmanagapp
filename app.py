import streamlit as st
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Connexion Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
objectifs_df = conn.read(worksheet="Objectifs")
sousobjectifs_df = conn.read(worksheet="SousObjectifs")
reflexions_df = conn.read(worksheet="Reflexions")

st.title("Bienvenue Alexandre sur ton application de définition et de suivi de tes objectifs")

if st.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()

# --------- SECTION 1 : Réflexion libre ---------
st.header("Réflexion libre sur tes objectifs")
reflexion_input = st.text_area(
    "Écris ici toutes tes idées, inspirations, questions, ou réflexions pour t'aider à définir tes objectifs.",
    height=200
)
if st.button("Enregistrer mes réflexions"):
    nouvelle_reflexion = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Texte": reflexion_input
    }
    reflexions_df = pd.concat([reflexions_df, pd.DataFrame([nouvelle_reflexion])], ignore_index=True)
    conn.update(worksheet="Reflexions", data=reflexions_df)
    st.success("Réflexion enregistrée dans Google Sheets !")

if not reflexions_df.empty:
    st.markdown("### Historique de tes réflexions")
    for idx, row in reflexions_df.sort_values("Date", ascending=False).iterrows():
        st.markdown(f"**{row.get('Date', '')}**")
        st.write(row.get('Texte', ''))
        st.markdown("---")

st.markdown("---")

# --------- SECTION 2 : Ajout d’un objectif de vie ---------
st.header("Ajouter un objectif de vie")
with st.form("ajout_objectif"):
    titre = st.text_input("Titre de l'objectif de vie")
    description = st.text_area("Description de l'objectif de vie")
    nb_annees = st.number_input(
        "Dans combien d'années souhaites-tu atteindre cet objectif ? (décimal possible)",
        min_value=0.1,
        max_value=20.0,
        value=1.0,
        step=0.1,
        format="%.1f"
    )
    date_echeance = st.date_input(
        "Date d'échéance (à renseigner toi-même)",
        value=date.today()
    )
    submit_obj = st.form_submit_button("Ajouter l'objectif de vie")
    if submit_obj and titre:
        nouvel_objectif = {
            "Titre": titre,
            "Description": description,
            "Durée (années)": nb_annees,
            "Date d'échéance": date_echeance.strftime('%Y-%m-%d'),
            "Avancement": ""  # L'avancement sera rempli plus tard
        }
        objectifs_df = pd.concat([objectifs_df, pd.DataFrame([nouvel_objectif])], ignore_index=True)
        conn.update(worksheet="Objectifs", data=objectifs_df)
        st.cache_data.clear()
        st.rerun()
        st.success("Objectif de vie ajouté dans Google Sheets !")

st.markdown("---")

# --------- SECTION 3 : Objectifs de vie actuels et sous-objectifs ---------
st.header("Objectifs de vie actuels")

if not objectifs_df.empty:
    for idx, row in objectifs_df.iterrows():
        titre = row.get("Titre", "")
        duree = row.get("Durée (années)", "")
        date_ech = row.get("Date d'échéance", "")
        description = row.get("Description", "")
        avancement = row.get("Avancement", "")

        # Titre en gras
        st.markdown(f"### {titre}")
        # Preview
        st.markdown("*Voir le détail*")

        # Détail dans un expander
        with st.expander("Détail de l'objectif"):
            st.write(f"**À atteindre dans {duree} an(s), pour le {date_ech}**")
            st.write(f"**Description :** {description}")

            # Champ pour mettre à jour l'avancement
            with st.form(f"maj_avancement_{idx}"):
                new_avancement = st.text_area(
                    "Où en es-tu dans la réalisation de cet objectif ?",
                    value=avancement,
                    key=f"avancement_{idx}"
                )
                submit_maj = st.form_submit_button("Mettre à jour l'avancement")
                if submit_maj:
                    objectifs_df.at[idx, "Avancement"] = new_avancement
                    conn.update(worksheet="Objectifs", data=objectifs_df)
                    st.success("Avancement mis à jour dans Google Sheets !")

            # Ajout de sous-objectifs pour cet objectif
            st.markdown("**Ajouter un sous-objectif**")
            with st.form(f"ajout_sous_objectif_{idx}"):
                sous_titre = st.text_input("Titre du sous-objectif", key=f"sous_titre_{idx}")
                sous_description = st.text_area("Description du sous-objectif", key=f"sous_description_{idx}")
                sous_nb_annees = st.number_input(
                    "Dans combien d'années souhaites-tu atteindre ce sous-objectif ? (décimal possible)",
                    min_value=0.1,
                    max_value=20.0,
                    value=1.0,
                    step=0.1,
                    format="%.1f",
                    key=f"sous_nb_annees_{idx}"
                )
                sous_date_echeance = st.date_input(
                    "Date d'échéance du sous-objectif (à renseigner toi-même)",
                    value=date.today(),
                    key=f"sous_date_echeance_{idx}"
                )
                sous_avancement = st.text_area(
                    "Où en es-tu dans la réalisation de ce sous-objectif ?",
                    key=f"sous_avancement_{idx}"
                )
                submit_sous_obj = st.form_submit_button("Ajouter le sous-objectif")
                if submit_sous_obj and sous_titre:
                    nouveau_sous_objectif = {
                        "ObjectifParent": titre,
                        "Titre": sous_titre,
                        "Description": sous_description,
                        "Durée (années)": sous_nb_annees,
                        "Date d'échéance": sous_date_echeance.strftime('%Y-%m-%d'),
                        "Avancement": sous_avancement
                    }
                    sousobjectifs_df = pd.concat([sousobjectifs_df, pd.DataFrame([nouveau_sous_objectif])], ignore_index=True)
                    conn.update(worksheet="SousObjectifs", data=sousobjectifs_df)
                    st.success("Sous-objectif ajouté dans Google Sheets !")

            # Affichage des sous-objectifs liés à cet objectif
            sous_obj = sousobjectifs_df[sousobjectifs_df["ObjectifParent"] == titre]
            if not sous_obj.empty:
                st.markdown("**Sous-objectifs associés :**")
                for _, sous_row in sous_obj.iterrows():
                    st.write(
                        "- {} : {} (À atteindre dans {} an(s), pour le {})".format(
                            sous_row.get('Titre', ''),
                            sous_row.get('Description', ''),
                            sous_row.get('Durée (années)', ''),
                            sous_row.get("Date d'échéance", "")
                        )
                    )
                    st.write(f"  Avancement : {sous_row.get('Avancement', '')}")
            st.markdown("---")
else:
    st.info("Aucun objectif de vie enregistré.")
