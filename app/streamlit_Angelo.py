# import streamlit as st
# import requests

# BACKEND_URL = "http://127.0.0.1:8000"

# def documentazione_page():
#     st.title("📄 Carica un documento PDF")

#     uploaded_file = st.file_uploader("Seleziona un file PDF", type=["pdf"])
#     if uploaded_file is not None:
#         st.write(f"📄 File caricato: {uploaded_file.name}")
#         files = {"file": uploaded_file.getvalue()}
#         response = requests.post(f"{BACKEND_URL}/upload_pdf/", files=files)
        
#         if response.status_code == 200:
#             st.success("✅ Documento salvato e analizzato con successo!")
#         else:
#             st.error(f"❌ Errore: {response.json().get('error')}")

# # if __name__ == "__main__":
# #     st.set_page_config(page_title="Riqualificazione Urbana AI")
# #     documentazione_page()

#  # 🔹 Dopo l'upload, mostra le ultime 5 righe del database
#     show_latest_projects()

# def show_latest_projects():
#     """Recupera e mostra gli ultimi 5 progetti salvati nel database"""
#     st.subheader("📊 Ultimi 5 Progetti Aggiunti")

#     try:
#         response = requests.get(f"{BACKEND_URL}/latest_projects/")
#         if response.status_code == 200:
#             data = response.json()
#             projects = data.get("latest_projects", [])

#             if projects:
#                 st.success("✅ Dati caricati con successo!")
#                 st.table(projects)  # Mostra i dati in una tabella
#             else:
#                 st.warning("⚠️ Nessun dato disponibile. Assicurati di aver caricato un documento.")
#         else:
#             st.error(f"❌ Errore nel recupero dati: {response.status_code}")
#     except requests.exceptions.RequestException as e:
#         st.error(f"❌ Errore di connessione: {e}")

# if __name__ == "__main__":
#     st.set_page_config(page_title="Riqualificazione Urbana AI")
#     documentazione_page()

import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://127.0.0.1:8000"

def documentazione_page():
    st.title("📄 Carica un documento PDF")

    uploaded_file = st.file_uploader("Seleziona un file PDF", type=["pdf"])
    
    if uploaded_file is not None:
        st.write(f"📄 File caricato: {uploaded_file.name}")
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{BACKEND_URL}/upload_pdf/", files=files)
        
        if response.status_code == 200:
            st.success("✅ Documento salvato e analizzato con successo!")
        else:
            st.error(f"❌ Errore: {response.json().get('error')}")
    
    # 🔹 Dopo l'upload, mostra le ultime 5 righe del database
    show_latest_projects()

# 🔹 Dopo l'upload, mostra le ultime 5 righe del database
    show_latest_projects()

def show_latest_projects():
    """Recupera e mostra gli ultimi 5 progetti salvati nel database"""
    st.subheader("📊 Ultimi 5 Progetti Aggiunti")

    try:
        response = requests.get(f"{BACKEND_URL}/latest_projects/")
        if response.status_code == 200:
            data = response.json()
            projects = data.get("latest_projects", []) # "projects" corrisponde a "all_projects"

            if projects:
                st.success("✅ Dati caricati con successo!")
                
                # ✅ Converti in DataFrame per Streamlit
                df = pd.DataFrame(projects)
                
                # ✅ Pulizia e conversione di `costo_milioni`
                if "costo_milioni" in df.columns:
                    df["costo_milioni"] = pd.to_numeric(df["costo_milioni"], errors="coerce")
                    df["costo_milioni"] = df["costo_milioni"].fillna(0.0)

                # ✅ Sostituisce i valori NaN con "N/A" solo per le colonne testuali
                df = df.astype(str).replace("nan", "N/A").replace("NaN", "N/A")

                # 🔹 Migliore visualizzazione con `st.dataframe()`
                st.dataframe(df, width=1200, height=400)
            else:
                st.warning("⚠️ Nessun dato disponibile. Assicurati di aver caricato un documento.")
        else:
            st.error(f"❌ Errore nel recupero dati: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Errore di connessione: {e}")


def tool_regenai_page():
    st.title("Tool ReGenAI - Riqualificazione Spazi Pubblici")

    with st.form("riqualifica_form"):
        st.subheader("Inserimento Dati Area da Riqualificare")

        problema = st.text_area("Problema che Affligge lo Spazio Pubblico")
        interventi = st.text_area("Interventi Previsti")
        tipologia = st.text_input("Tipologia del Progetto")
        benefici_sociali = st.text_area("Benefici Sociali Attesi")
        benefici_economici = st.text_area("Benefici Economici Attesi")
        nome = st.text_input("Nome del Progetto (o un termine chiave)")
        sostenibilita = st.text_area("Aspetti di Sostenibilità")
        citta = st.text_input("Città del Progetto")
        paese = st.text_input("Paese del Progetto")
        superficie = st.number_input("Superficie in mq", min_value=1)
        costo = st.number_input("Costo in Milioni", min_value=0.0)

        submitted = st.form_submit_button("Trova Progetti Simili")

        if submitted:
            # 📌 Creiamo il JSON da inviare al backend
            dati_progetto = {
                "problema": problema,
                "interventi": interventi,
                "tipologia": tipologia,
                "benefici_sociali": benefici_sociali,
                "benefici_economici": benefici_economici,
                "nome": nome,
                "sostenibilita": sostenibilita,
                "citta": citta,
                "paese": paese,
                "superficie_mq": superficie,
                "costo_milioni": costo
            }

            # 📌 Chiamiamo il backend FastAPI
            with st.spinner("🔍 Ricerca in corso..."):
                response = requests.post(f"{BACKEND_URL}/match_project/", json=dati_progetto)

            # 📌 Gestiamo la risposta
            if response.status_code == 200:
                risultati = response.json().get("progetti_simili", [])
                st.success("✅ Progetti simili trovati!")

                # 📌 Mostriamo i risultati
                if risultati:
                    for progetto in risultati:
                        st.markdown(f"**{progetto['nome']}** - {progetto['citta']}, {progetto['paese']}")
                        st.write(f"📏 Superficie: {progetto['superficie_mq']} mq")
                        st.write(f"💰 Costo: {progetto['costo_milioni']} milioni")
                        st.write(f"🔍 Similarità: {round(progetto['similarita'] * 100, 2)}%")
                        st.write("---")
                else:
                    st.warning("⚠ Nessun progetto simile trovato.")

            else:
                st.error(f"❌ Errore: {response.status_code}")


if __name__ == "__main__":
    st.set_page_config(page_title="Riqualificazione Urbana AI")
    documentazione_page()
    tool_regenai_page()


