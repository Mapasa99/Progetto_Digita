import streamlit as st
import time
import base64
from reportlab.pdfgen import canvas
from io import BytesIO
from pathlib import Path
import uuid # Importa la libreria per UUID
import random
import string # Importa string
import folium # Importa folium
from streamlit_folium import folium_static # Importa folium_static
import folium.plugins # Importa i plugin di Folium
import pandas as pd # Importa pandas
import requests
import tempfile
import json

# Funzioni per le icone e le immagini
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

# Immagini e dati del Comune di Napoli
map_placeholder_url = "https://www.napoliclick.it/wp-content/uploads/2018/12/mappa-interattiva-napoli-street-view.jpg"
comune_nome = "Comune di Napoli"
comune_indirizzo = "Piazza Municipio, 1, 80133 Napoli NA"


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


    for i in range(0, len(projects), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(projects):
                project = projects[i + j]
                with cols[j]:
                    title = project.get("titolo") or project.get("nome", "Senza Titolo")
                    st.subheader(title)
                    # image_url = project.get("immagine")
                    # if image_url:
                    #     st.image(image_url, use_container_width=True, caption=project.get("descrizione_breve", ""))
                    # else:
                    #     st.info("Immagine non disponibile.")
                    st.write(f"**Descrizione Breve:** {project.get('descrizione_breve', 'N/A')}")
                    for key, value in project.items():
                        if key not in ["immagine", "coordinate", "descrizione_breve", "titolo", "nome"]:
                            st.write(f"**{key.replace('_', ' ').title()}:** {value if pd.notna(value) else 'N/A'}")
                    st.markdown("---")

def dettagli_progetto_page():
    project = st.session_state.get('selected_project')
    if not project:
        st.error("Progetto non trovato.")
        return

    st.title(f"Dettagli Progetto: {project.get('nome') or project.get('titolo', 'Senza Titolo')}")
    image_path = project.get("immagine")
    if image_path:
        st.image(image_path, use_container_width=True, caption=project.get('nome') or project.get('titolo', 'Senza Titolo'))
    else:
        st.info("Immagine non disponibile.")

    st.subheader("Informazioni Dettagliate")
    for key, value in project.items():
        if key not in ["immagine", "coordinate", "descrizione_breve", "titolo", "nome"]:
            st.write(f"**{key.replace('_', ' ').title()}:** {value if pd.notna(value) else 'N/A'}")

    if st.button("Torna alla Documentazione"):
        st.session_state['page'] = 'documentazione'
        st.rerun()


# Funzione per generare il PDF del progetto di successo
def generate_project_success_pdf(form_data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Progetto di Successo Corrispondente")
    p.drawString(100, 700, "Comune di Napoli - ReGenAI Tool")
    p.drawString(100, 650, "---------------------------------------")
    p.drawString(100, 600, f"Tipologia Intervento: {form_data['descrizione_intervento']}")
    p.drawString(100, 580, f"Superficie: {form_data['superficie']} mq")
    # ... puoi aggiungere altri dati rilevanti qui ...
    p.drawString(100, 500, "Progetto Ottenuto con Corrispondenza Migliore!")
    p.save()
    buffer.seek(0)
    pdf_bytes = buffer.read()
    return base64.b64encode(pdf_bytes).decode()

# Funzione per generare il PDF del report
def generate_report_pdf(form_data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Report di Riqualificazione Area")
    p.drawString(100, 730, "Comune di Napoli - ReGenAI Tool")
    p.drawString(100, 700, "---------------------------------------")

    y_position = 680
    for key, value in form_data.items():
        y_position -= 20
        p.drawString(100, y_position, f"{key.replace('_', ' ').title()}: {value}")

    p.drawString(100, 100, "Report generato con AI - Solo a scopo informativo") # Avviso AI
    p.save()
    buffer.seek(0)
    pdf_bytes = buffer.read()
    return base64.b64encode(pdf_bytes).decode()


# def tool_regenai_page():
#     st.title("Tool ReGenAI - Riqualificazione Spazi Pubblici")

#     with st.form("riqualifica_form"):
#         st.subheader("Inserimento Dati Area da Riqualificare")

#         problema = st.text_area("Problema che Affligge lo Spazio Pubblico")
#         interventi = st.text_area("Interventi Previsti")
#         tipologia = st.text_input("Tipologia del Progetto")
#         benefici_sociali = st.text_area("Benefici Sociali Attesi")
#         benefici_economici = st.text_area("Benefici Economici Attesi")
#         nome = st.text_input("Nome del Progetto (o un termine chiave)")
#         sostenibilita = st.text_area("Aspetti di Sostenibilità")
#         citta = st.text_input("Città del Progetto")
#         paese = st.text_input("Paese del Progetto")
#         superficie = st.number_input("Superficie in mq", min_value=1)
#         costo = st.number_input("Costo in Milioni", min_value=0.0)

#         submitted = st.form_submit_button("Trova Progetti Simili")

#         if submitted:
#             # 📌 Creiamo il JSON da inviare al backend
#             dati_progetto = {
#                 "problema": problema,
#                 "interventi": interventi,
#                 "tipologia": tipologia,
#                 "benefici_sociali": benefici_sociali,
#                 "benefici_economici": benefici_economici,
#                 "nome": nome,
#                 "sostenibilita": sostenibilita,
#                 "citta": citta,
#                 "paese": paese,
#                 "superficie_mq": superficie,
#                 "costo_milioni": costo
#             }

#             # 📌 Chiamiamo il backend FastAPI
#             with st.spinner("🔍 Ricerca in corso..."):
#                 response = requests.post(f"{BACKEND_URL}/match_project/", json=dati_progetto)

#             # 📌 Gestiamo la risposta
#             if response.status_code == 200:
#                 risultati = response.json().get("progetti_simili", [])
#                 st.success("✅ Progetti simili trovati!")

#                 # 📌 Mostriamo i risultati
#                 if risultati:
#                     for progetto in risultati:
#                         st.markdown(f"**{progetto['nome']}** - {progetto['citta']}, {progetto['paese']}")
#                         st.write(f"📏 Superficie: {progetto['superficie_mq']} mq")
#                         st.write(f"💰 Costo: {progetto['costo_milioni']} milioni")
#                         st.write(f"🔍 Similarità: {round(progetto['similarita'] * 100, 2)}%")
#                         st.write("---")
#                 else:
#                     st.warning("⚠ Nessun progetto simile trovato.")

#             else:
#                 st.error(f"❌ Errore: {response.status_code}")


#     # 📌 Aggiungi il pulsante per generare il report PDF se abbiamo i risultati
#     if "top_5_progetti" in st.session_state:
#         st.subheader("📝 Genera Report PDF")

#         if st.button("📄 Crea Report di Riqualificazione"):
#             with st.spinner("Generazione del report in corso..."):
#                 response = requests.post(
#     f"{BACKEND_URL}/generate_report/",
#     json={"progetti": st.session_state["top_5_progetti"].to_dict(orient="records")}
# )


#             if response.status_code == 200:
#                 pdf_path = response.json()["pdf_path"]
#                 st.success("✅ Report generato con successo!")

#                 with open(pdf_path, "rb") as file:
#                     st.download_button("📥 Scarica il Report", file, file_name="report_riqualificazione.pdf", mime="application/pdf")
#             else:
#                 st.error(f"❌ Errore: {response.json().get('detail', 'Errore sconosciuto')}")

# 

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
                risultati = response.json().get("progetti_simili",)
                st.success("✅ Progetti simili trovati!")

                # 📌 Mostriamo i risultati e memorizziamo i primi 5 nello session state
                if risultati:
                    st.session_state["top_5_progetti"] = risultati[:5]  # Prendi i primi 5 risultati
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

    # 📌 Aggiungi il pulsante per generare il report PDF se abbiamo i risultati
    if "top_5_progetti" in st.session_state:
        st.subheader("📝 Genera Report PDF")

        if st.button("📄 Crea Report di Riqualificazione"):
            with st.spinner("Generazione del report in corso..."):
                # Assicurati che st.session_state["top_5_progetti"] sia una lista di dizionari
                report_data = {"progetti": st.session_state["top_5_progetti"]}
                response = requests.post(
                    f"{BACKEND_URL}/generate_report/",
                    json=report_data
                )
                # if response.status_code == 200:
                #     try:
                #         # Supponiamo che il backend restituisca il percorso del file PDF nel JSON
                #         pdf_path = response.json().get("pdf_path")
                #         #pdf_path(f'Ho creato il file {pdf_path}')
                #         pdf_path = Path(r"C:\Users\valen\Desktop\Team_7\Progetto_Digita-1\app\report_riqualificazione.pdf")
                #         if pdf_path:
                #             print('Devo fare il download del file pdf')
                #          #   with pdf_path.open("rb") as file:
                #           #      st.download_button("📥 Scarica il Report", file, file_name="report_riqualificazione.pdf", mime="application/pdf")
                #         else:
                #             st.error("❌ Errore: Percorso del file PDF non trovato nella risposta del backend.")
                #     except Exception as e:
                #         st.error(f"❌ Errore durante la gestione della risposta del report: {e}")
                # else:
                #     st.error(f"❌ Errore nella generazione del report: {response.status_code} - {response.json().get('detail', 'Errore sconosciuto')}")
                if response.status_code == 200:
                    try:
                        pdf_content = response.content
                        st.success("✅ Report generato con successo!")
                        if pdf_content:
                            st.download_button("📥 Scarica il Report", pdf_content, file_name="report_riqualificazione.pdf", mime="application/pdf")
                        else:
                            st.error("❌ Errore: Contenuto del file PDF non ricevuto dal backend.")
                    except Exception as e:
                        st.error(f"❌ Errore durante la gestione della risposta del report: {e}")


def statistiche_page(): # NUOVA FUNZIONE PER LA PAGINA STATISTICHE
    st.title("Statistiche") # Titolo principale della pagina

    st.subheader("Panoramica Generale Progetti") # Sottotitolo sezione

    col1, col2 = st.columns(2) # Crea due colonne affiancate

    with col1: # Prima colonna
        st.markdown("**Progetti Totali Inseriti:**") # Titolo statistica
        st.markdown("## 150") # Numero statistica (placeholder)
        st.markdown("<p style='font-size: smaller; color: grey;'>Aggiornato al 15/03/2025</p>", unsafe_allow_html=True) # Data aggiornamento

    with col2: # Seconda colonna
        st.markdown("**Progetti in Fase di Valutazione:**") # Titolo statistica
        st.markdown("## 35") # Numero statistica (placeholder)
        st.markdown("<p style='font-size: smaller; color: grey;'>Aggiornato al 15/03/2025</p>", unsafe_allow_html=True) # Data aggiornamento

    st.markdown("---") # Linea di separazione

    st.subheader("Tipologie di Intervento più Comuni") # Sottotitolo sezione

    col3, col4 = st.columns(2) # Altre due colonne

    with col3: # Terza colonna (a sinistra)
        st.markdown("**Riqualificazione Piazze e Spazi Pubblici:**") # Titolo statistica
        st.markdown("## 45%") # Percentuale (placeholder)
        st.markdown("<p style='font-size: smaller; color: grey;'>Basato sugli ultimi 12 mesi</p>", unsafe_allow_html=True) # Periodo di riferimento

    with col4: # Quarta colonna (a destra)
        st.markdown("**Creazione e Restauro Parchi Urbani:**") # Titolo statistica
        st.markdown("## 30%") # Percentuale (placeholder)
        st.markdown("<p style='font-size: smaller; color: grey;'>Basato sugli ultimi 12 mesi</p>", unsafe_allow_html=True) # Periodo di riferimento

    st.markdown("---") # Altra linea di separazione

    st.subheader("Distribuzione Geografica Progetti") # Sottotitolo sezione # Modificato titolo sezione

    # Mappa Folium centrata su Napoli (o altra posizione predefinita)
    napoli_coords = [40.8358, 14.2487] # Coordinate di Napoli (centro)
    m_statistiche = folium.Map(location=napoli_coords, zoom_start=12, tiles="CartoDB positron") # Mappa Folium

    # **IMPORTANTE**: Dato che `sample_projects` ora CONTIENE coordinate geografiche,
    # possiamo usarle per posizionare i marker correttamente sulla mappa.


def main():
    st.set_page_config(page_title="ReGenAI Tool - Comune di Napoli", page_icon=":cityscape:")
    local_css("style.css")

    st.session_state['logged_in'] = st.session_state.get('logged_in', False) # Inizializza logged_in a False se non esiste
    st.session_state['form_data'] = None # **INIZIALIZZA form_data a None QUI!**


    # --- SIDEBAR MENU ---
    st.sidebar.image("images/logo_comune_di_napoli.png", width=120) # Immagine LOCALE logo
    st.sidebar.title(comune_nome)
    st.sidebar.write(comune_indirizzo)
    st.sidebar.markdown("---")

    if st.sidebar.button("Tool ReGenAI", key='tool_regenai_button'): # Bottone Tool ReGenAI - sempre abilitato
        st.session_state['page'] = 'tool_regenai'
        st.rerun()

    if st.sidebar.button("Documentazione", key='documentazione_button'): # Bottone Documentazione - sempre abilitato
        st.session_state['page'] = 'documentazione'
        st.rerun()

    if st.sidebar.button("Statistiche", key='statistiche_button'): # NUOVO Bottone Statistiche
        st.session_state['page'] = 'statistiche'
        st.rerun()


    # SEZIONE LOGIN DIPENDENTE - SPOSTATA IN FONDO AL MENU SIDEBAR
    st.sidebar.markdown("---") # Separatore prima del Login Dipendente
    st.sidebar.header("Login Dipendente")

    # Codice identificativo univoco del dipendente (massimo 6 char alfanumerici)
    dipendente_id = st.session_state.get('dipendente_id')
    if not dipendente_id:
        # Genera ID alfanumerico di 6 caratteri se non esiste
        characters = string.ascii_letters + string.digits
        dipendente_id = ''.join(random.choice(characters) for i in range(6))
        st.session_state['dipendente_id'] = dipendente_id
    st.sidebar.write(f"ID Dipendente: `{dipendente_id}`") # Mostra ID completo (ora breve)

    dipendente_foto_path = "images/dipendente_foto.png" # Immagine LOCALE
    st.sidebar.image(dipendente_foto_path, width=100)
    st.sidebar.write(f"Dipendente: Mario Rossi") # Nome dipendente statico

    login_clicked = st.sidebar.button("Login") # Bottone Login
    if login_clicked: # Se cliccato Login
        st.session_state['logged_in'] = True # Setta flag login a True
        st.sidebar.success("Login effettuato con successo!") # Messaggio successo
        st.rerun() # Ricarica per mostrare contenutoTool e Documentazione

    if st.sidebar.button("Logout"):
        st.sidebar.success("Logout effettuato")
        st.session_state['logged_in'] = False # Flag di logout
        st.session_state['step'] = None # Resetta step tool
        st.session_state['form_data'] = None # Resetta dati form
        st.session_state['uploaded_files'] = None # Resetta file documentazione
        st.session_state['dipendente_id'] = None # Resetta ID dipendente
        st.session_state['page'] = 'tool_regenai' # Ritorna alla pagina tool (o home)
        st.rerun() # Ricarica l'app per riflettere il logout


    # Pagina e step vengono gestiti SEMPRE, indipendentemente dal login
    if 'page' not in st.session_state:
        st.session_state['page'] = 'tool_regenai'
    if 'step' not in st.session_state:
        st.session_state['step'] = None

    page = st.session_state['page']

    if page == "tool_regenai":
        tool_regenai_page()
    elif page == "documentazione":
        documentazione_page()
    elif page == "dettagli_progetto":
        dettagli_progetto_page()
    elif page == "statistiche": # NUOVA PAGINA STATISTICHE
        statistiche_page()
    # RIMOSSA CONDIZIONE if st.session_state.get('logged_in'): - le pagine sono sempre mostrate

    # footer_comune_napoli() # Chiama la funzione per mostrare il footer in fondo  <-- COMMENTATA/RIMOSSA
    pass #  Se commenti footer_comune_napoli(), aggiungi 'pass' per evitare errori di indentazione se è l'ultima riga

if __name__ == "__main__":
    main()