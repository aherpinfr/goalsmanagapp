import streamlit as st
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --------- CONNEXION GOOGLE SHEETS ---------
conn = st.connection("gsheets", type=GSheetsConnection)

# Lecture des worksheets (onglets)
objectifs_df = conn.read(worksheet="Objectifs")
sousobjectifs_df = conn.read(worksheet="SousObjectifs")
reflexions_df = conn.read(worksheet="Reflexions")

# --------- PAGE D'ACCUEIL ---------
st.title("Bienvenue Alexandre sur ton application de définition et de suivi de tes objectifs")

# --------- SECTION REFLEXION LIBRE ---------
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
    conn.write(reflexions_df, worksheet="Reflexions")
    st.success("Réflexion enregistrée dans Google Sheets !")

st.markdown("---")

# --------- NAVIGATION ---------
onglet = st.sidebar.radio("Navigation", ["Objectifs de vie", "Sous-objectifs", "Réflexions"])

# --------- OBJECTIFS DE VIE ---------
if onglet == "Objectifs de vie":
    st.header("Ajouter un objectif de vie")
    with st.form("ajout_objectif"):
        titre = st.text_input("Titre de l'objectif de vie")
        description = st.text_area("Description de l'objectif de vie")
        nb_annees = st.number_input(
            "Dans combien d'années souhaites-tu atteindre cet objectif ? (décimal possible)",
            min_value=0.1, max_value=20.0, value=1.0, step=0.1, format="%.1f"
        )
        date_echeance = st.date_input(
            "Date d'échéance (à renseigner toi-même)",
            value=date.today()
        )
        avancement = st.text_area("Où en es-tu dans la réalisation de cet objectif ?")
        submit_obj = st.form_submit_button("Ajouter l'objectif de vie")
        if submit_obj and titre:
            nouvel_objectif = {
                "Titre": titre,
                "Description": description,
                "Durée (années)": nb_annees,
                "Date d'échéance": date_echeance.strftime('%Y-%m-%d'),
                "Avancement": avancement
            }
            objectifs_df = pd.concat([objectifs_df, pd.DataFrame([nouvel_objectif])], ignore_index=True)
            conn.write(objectifs_df, worksheet="Objectifs")
            st.success("Objectif de vie ajouté dans Google Sheets !")

    st.markdown("### Tes objectifs de vie")
    if not objectifs_df.empty:
        for idx, row in objectifs_df.iterrows():
            titre = row.get("Titre", "")
            duree = row.get("Durée (années)", "")
            date_ech = row.get("Date d'échéance", "")
            description = row.get("Description", "")
            avancement = row.get("Avancement", "")
            st.subheader(f"{titre}")
            st.write(f"**À atteindre dans {duree} an(s), pour le {date_ech}**")
            st.write(description)
            st.write(f"**Avancement :** {avancement}")
            st.markdown("---")
    else:
        st.info("Aucun objectif de vie enregistré.")

# --------- SOUS-OBJECTIFS ---------
if onglet == "Sous-objectifs":
    st.header("Ajouter un sous-objectif")
    if objectifs_df.empty:
        st.warning("Ajoute d'abord un objectif de vie avant de créer un sous-objectif.")
    else:
        with st.form("ajout_sous_objectif"):
            objectif_parent = st.selectbox(
                "À quel objectif de vie rattacher ce sous-objectif ?",
                objectifs_df["Titre"].tolist()
            )
            sous_titre = st.text_input("Titre du sous-objectif")
            sous_description = st.text_area("Description du sous-objectif")
            sous_nb_annees = st.number_input(
                "Dans combien d'années souhaites-tu atteindre ce sous-objectif ? (décimal possible)",
                min_value=0.1, max_value=20.0, value=1.0, step=0.1, format="%.1f"
            )
            sous_date_echeance = st.date_input(
                "Date d'échéance du sous-objectif (à renseigner toi-même)",
                value=date.today()
            )
            sous_avancement = st.text_area("Où en es-tu dans la réalisation de ce sous-objectif ?")
            submit_sous_obj = st.form_submit_button("Ajouter le sous-objectif")
            if submit_sous_obj and sous_titre:
                nouveau_sous_objectif = {
                    "ObjectifParent": objectif_parent,
                    "Titre": sous_titre,
                    "Description": sous_description,
                    "Durée (années)": sous_nb_annees,
                    "Date d'échéance": sous_date_echeance.strftime('%Y-%m-%d'),
                    "Avancement": sous_avancement
                }
                sousobjectifs_df = pd.concat([sousobjectifs_df, pd.DataFrame([nouveau_sous_objectif])], ignore_index=True)
                conn.write(sousobjectifs_df, worksheet="SousObjectifs")
                st.success("Sous-objectif ajouté dans Google Sheets !")

    st.markdown("### Tes sous-objectifs")
    if not sousobjectifs_df.empty:
        for idx, row in sousobjectifs_df.iterrows():
            titre = row.get("Titre", "")
            objectif_parent = row.get("ObjectifParent", "")
            description = row.get("Description", "")
            duree = row.get("Durée (années)", "")
            date_ech = row.get("Date d'échéance", "")
            avancement = row.get("Avancement", "")
            st.subheader(f"{titre} (lié à : {objectif_parent})")
            st.write(f"**Description :** {description}")
            st.write(f"**À atteindre dans {duree} an(s), pour le {date_ech}**")
            st.write(f"**Avancement :** {avancement}")
            st.markdown("---")
    else:
        st.info("Aucun sous-objectif enregistré.")

# --------- REFLEXIONS ---------
if onglet == "Réflexions":
    st.header("Historique de tes réflexions")
    if not reflexions_df.empty:
        for idx, row in reflexions_df.sort_values("Date", ascending=False).iterrows():
            date_ref = row.get("Date", "")
            texte = row.get("Texte", "")
            st.markdown(f"**{date_ref}**")
            st.write(texte)
            st.markdown("---")
    else:
        st.info("Aucune réflexion enregistrée.")
