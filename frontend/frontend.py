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

BACKEND_URL = "http://127.0.0.1:8000"

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

# Nome del file CSV
CSV_FILE = "data/progetti_coordinate2.csv"

def load_projects_from_csv():
    try:
        df = pd.read_csv(CSV_FILE, sep=';')
        # Converti il DataFrame in una lista di dizionari nel formato atteso
        projects = []
        for index, row in df.iterrows():
            try:
                coordinate_str = row['coordinate'].strip("[]").split(',')
                coordinate = [float(coord.strip()) for coord in coordinate_str]
            except (AttributeError, ValueError):
                coordinate = None  # Gestisci il caso di coordinate non valide

            project = {
                "nome": row['nome'],
                "citta": row['citta'],
                "paese": row['paese'],
                "anno": int(row['anno']) if pd.notna(row['anno']) else None,
                "superficie_mq": int(row['superficie_mq']) if pd.notna(row['superficie_mq']) else None,
                "tipologia": row['tipologia'],
                "problema": row['problema'],
                "interventi": row['interventi'],
                "costo_milioni": float(row['costo_milioni']) if pd.notna(row['costo_milioni']) else None,
                "finanziamento": row['finanziamento'],
                "benefici_sociali": row['benefici_sociali'],
                "benefici_economici": row['benefici_economici'],
                "sostenibilita": row['sostenibilita'],
                "coordinate": coordinate
            }
            projects.append(project)
        return projects
    except FileNotFoundError:
        return []

def save_project_to_csv(new_project):
    df = pd.DataFrame([new_project])
    df.to_csv(CSV_FILE, mode='a', header=not Path(CSV_FILE).exists(), index=False, sep=';')

import streamlit as st
import tempfile
import requests
import json

def documentazione_page():
    st.title("Documentazione Progetti di Successo")

    uploaded_file = st.file_uploader("Seleziona un file PDF", type=["pdf"])
    
    if uploaded_file is not None:
        st.write(f"📄 File caricato: {uploaded_file.name}")
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{BACKEND_URL}/upload_pdf/", files=files)
        
        if response.status_code == 200:
            st.success("✅ Documento salvato e analizzato con successo!")
        else:
            st.error(f"❌ Errore: {response.json().get('error')}")

    with st.form("aggiungi_progetto_form"):
        st.subheader("Aggiungi un Nuovo Progetto di Successo")
        nome = st.text_input("Nome del Progetto")
        citta = st.text_input("Città")
        paese = st.text_input("Paese")
        anno = st.number_input("Anno", min_value=1900, max_value=2050, step=1)
        superficie_mq = st.number_input("Superficie (mq)", min_value=1)
        tipologia = st.text_input("Tipologia di Intervento")
        problema = st.text_area("Problema Affliggeva lo Spazio")
        interventi = st.text_area("Interventi Realizzati")
        costo_milioni = st.number_input("Costo (Milioni)", min_value=0.0)
        finanziamento = st.text_input("Finanziamento")
        benefici_sociali = st.text_area("Benefici Sociali")
        benefici_economici = st.text_area("Benefici Economici")
        sostenibilita = st.text_area("Sostenibilità")
        coordinate_str = st.text_input("Coordinate (latitudine, longitudine - es: 40.8, 14.2)")
        submitted_new_project = st.form_submit_button("Aggiungi Progetto")

        if submitted_new_project:
            try:
                lat, lon = map(float, coordinate_str.split(','))
                coordinate = [lat, lon]
                new_project_data = {
                    "nome": nome,
                    "citta": citta,
                    "paese": paese,
                    "anno": anno,
                    "superficie_mq": superficie_mq,
                    "tipologia": tipologia,
                    "problema": problema,
                    "interventi": interventi,
                    "costo_milioni": costo_milioni,
                    "finanziamento": finanziamento,
                    "benefici_sociali": benefici_sociali,
                    "benefici_economici": benefici_economici,
                    "sostenibilita": sostenibilita,
                    "coordinate": coordinate
                }
                save_project_to_csv(new_project_data)
                st.success(f"Progetto '{nome}' aggiunto con successo!")
            except ValueError:
                st.error("Formato coordinate non valido. Inserisci latitudine e longitudine separate da una virgola (es: 40.8, 14.2).")

    st.subheader("Progetti di Successo Preesistenti")
    # Carica i progetti dal CSV
    csv_projects = load_projects_from_csv()

    # Combina i progetti di esempio con quelli del CSV
    all_projects = csv_projects

    if not all_projects:
        st.info("Nessun progetto di successo disponibile.")
        return

    for i in range(0, len(all_projects), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(all_projects):
                project = all_projects[i + j]
                with cols[j]:
                    title = project.get("titolo") or project.get("nome", "Senza Titolo")
                    st.subheader(title)
                    image_url = project.get("immagine")
                    if image_url:
                        st.image(image_url, use_container_width=True, caption=project.get("descrizione_breve", ""))
                    else:
                        st.info("Immagine non disponibile.")
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


def tool_regenai_page():
    st.title("Tool ReGenAI - Riqualificazione Spazi Pubblici")

    # Mappa Folium centrata su Napoli - MODIFICA TILES QUI!
    napoli_coords = [40.8358, 14.2487]  # Coordinate di Napoli, centro città circa

    # Opzioni di Tiles che puoi provare
    tiles_style = "CartoDB positron"

    m = folium.Map(location=napoli_coords, zoom_start=12, tiles=tiles_style, **{'position': 'topright'})
    folium.plugins.Fullscreen(position='topright').add_to(m)

    # Zone/Progetti preimpostati
    project_zones = [
        # ... (lista project_zones come prima) ...
         {
             "nome": "Scampia",
             "coordinate": [40.9099, 14.2348], # Scampia (Vele abbattute - area riqualificazione)
             "descrizione": "Progetto di riqualificazione sociale e urbana nel quartiere Scampia, con nuove aree verdi e servizi."
         }
        # ... puoi aggiungere altre zone preimpostate qui ...
    ]

    for zona in project_zones:
        folium.Marker(
            zona["coordinate"],
            popup=f"<b>{zona['nome']}</b><br>{zona['descrizione']}",
            tooltip=zona["nome"]
        ).add_to(m)

    folium_static(m)

    with st.form("riqualifica_form"):
        st.subheader("Inserimento Dati Area da Riqualificare")

        descrizione_intervento = st.text_area("Descrizione della Tipologia di Intervento", help="Descrivi in dettaglio il tipo di intervento di riqualificazione previsto (es. rifacimento pavimentazione, creazione area verde, restauro edificio storico, ecc.)")
        superficie = st.number_input("Superficie in Metri Quadri", min_value=1, help="Inserisci la superficie totale dell'area da riqualificare espressa in metri quadri.")
        problema = st.text_area("Problema che Affligge lo Spazio Pubblico", help="Descrivi la problematica principale che affligge attualmente lo spazio pubblico da riqualificare (es. degrado, mancanza di illuminazione, scarsa sicurezza, inutilizzo, ecc.)")

        # Menu a tendina "Fondi a Disposizione"
        fondi_options = [
            "FESR - Sviluppo Regionale",
            "FSE+ - Fondo Sociale Europeo Plus",
            "PNRR - Piano Nazionale di Ripresa e Resilienza",
            "Horizon Europe - Programma quadro",
            "LIFE - Ambiente e clima",
            "Europa Creativa",
            "Nessun finanziamento europeo",
            "Altro (specifica)"
        ]
        fondi_scelti = st.selectbox("Fondi a Disposizione", options=fondi_options, help="Seleziona i fondi disponibili per il progetto. Se non elencati, scegli 'Altro (specifica)' e inserisci nel campo sottostante.")
        fondi = fondi_scelti
        if fondi_scelti == "Altro (specifica)":
            fondi_personalizzati = st.text_input("Specifica altri Fondi a Disposizione", value="", help="Specifica qui altri fondi non presenti nella lista precedente.")
            if fondi_personalizzati:
                fondi = f"Altro: {fondi_personalizzati}"

        finanziamenti_europei = st.text_input("Finanziamenti Europei Disponibili (aggiuntivi)", help="Specifica SE sono disponibili ALTRI finanziamenti europei per questo progetto e, se sì, quali (es. fondi POR, FESR, PNRR, ecc.) - opzionale")
        benefici_sociali = st.text_area("Benefici Sociali Attesi", help="Descrivi i benefici sociali che si prevedono di ottenere con la riqualificazione (es. miglioramento della qualità della vita, aumento della fruibilità, inclusione sociale, ecc.)")
        benefici_economici = st.text_area("Benefici Economici Attesi", help="Descrivi i benefici economici che si prevedono di ottenere con la riqualificazione (es. aumento del valore immobiliare, sviluppo commerciale, incremento turistico, ecc.)")
        sostenibilita = st.text_area("Sostenibilità dell'Intervento", help="Descrivi gli aspetti di sostenibilità ambientale previsti nell'intervento (es. materiali eco-compatibili, risparmio energetico, recupero acque piovane, aree verdi, ecc.)")
        output_desiderato = st.text_area("Output Desiderato", help="Descrivi l'output finale che si vuole ottenere con il progetto di riqualificazione (es. parco pubblico attrezzato, piazza rinnovata, edificio restaurato e riutilizzato, ecc.)")

        submitted = st.form_submit_button("Invia")
        if submitted:
            st.session_state['form_data'] = {
                "descrizione_intervento": descrizione_intervento,
                "superficie": superficie,
                "problema": problema,
                "fondi": fondi,
                "finanziamenti_europei": finanziamenti_europei,
                "benefici_sociali": benefici_sociali,
                "benefici_economici": benefici_economici,
                "sostenibilita": sostenibilita,
                "output_desiderato": output_desiderato,
            }
            st.session_state['step'] = 'conferma'
            st.rerun()

    if st.session_state.get('step') == 'conferma':
        st.subheader("Conferma Dati Inseriti")
        if st.session_state['form_data'] is not None: # Aggiunto controllo per evitare errore NoneType
            for key, value in st.session_state['form_data'].items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

        conferma_button = st.button("Conferma")
        if conferma_button:
            st.session_state['step'] = 'loading_progetto'
            st.rerun()

    if st.session_state.get('step') == 'loading_progetto':
        with st.spinner("Sto cercando il progetto di successo più adatto a te..."):
            time.sleep(5)
        st.success("Ecco il progetto che ottenuto la corrispondenza migliore:")

        # Genera PDF progetto di successo **(SPOSTATO QUI!)**
        project_success_pdf_base64 = generate_project_success_pdf(st.session_state['form_data'])
        st.session_state['project_pdf_data'] = project_success_pdf_base64 # SALVA il PDF progetto in session_state
        pdf_display = f'<iframe src="data:application/pdf;base64,{project_success_pdf_base64}" width="700" height="700" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: smaller;'>Progetto Simile - Corrispondenza del 90%</p>", unsafe_allow_html=True)

        st.session_state['step'] = 'project_pdf_loaded' # Step dopo PDF progetto caricato


    if st.session_state.get('step') == 'project_pdf_loaded':
        if st.button("Genera Report"):
            st.session_state['step'] = 'loading_report'
            st.rerun()

    if st.session_state.get('step') == 'loading_report':
        with st.spinner("Sto creando il report per aiutarti nel tuo progetto di riqualificazione..."):
            time.sleep(5)
        st.success("Ecco il report per la riqualificazione dell’area da te inserita:")

        # Genera PDF report **(NESSUNA MODIFICA QUI)**
        report_pdf_base64 = generate_report_pdf(st.session_state['form_data'])
        st.session_state['report_pdf_data'] = report_pdf_base64
        st.session_state['step'] = 'report_pdf_loaded'


    if st.session_state.get('step') == 'report_pdf_loaded':
        st.subheader("Documenti Generati")

        st.write("**Progetto di Successo Simile:**")
        project_pdf_display = f'<iframe src="data:application/pdf;base64,{st.session_state['project_pdf_data']}" width="700" height="700" type="application/pdf"></iframe>'
        st.markdown(project_pdf_display, unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: smaller;'>Progetto Simile - Corrispondenza del 90%</p>", unsafe_allow_html=True)

        st.write(" ")

        st.write("**Report di Riqualificazione Area:**")
        report_pdf_display = f'<iframe src="data:application/pdf;base64,{st.session_state['report_pdf_data']}" width="700" height="700" type="application/pdf"></iframe>'
        st.markdown(report_pdf_display, unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: smaller;'>Report AI - Solo scopo informativo</p>", unsafe_allow_html=True)

        st.session_state['step'] = None


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

    # Aggiungi marker per ogni progetto in sample_projects (USANDO COORDINATE REALI)
    all_projects = load_projects_from_csv()
    for progetto in all_projects:
        coords = progetto.get('coordinate')
        nome_progetto = progetto.get('nome') or progetto.get('titolo', 'Senza Nome')
        descrizione = progetto.get('descrizione_breve', 'N/A')
        if coords:
            folium.Marker(
                coords, # **USA COORDINATE DEL PROGETTO!** - Ora funzionanti se hai aggiornato sample_projects
                popup=f"<b>{nome_progetto}</b><br>{descrizione}", # Popup con titolo e descrizione
                tooltip=nome_progetto # Tooltip al passaggio del mouse
            ).add_to(m_statistiche)

def main():
    st.set_page_config(page_title="ReGenAI Tool - Comune di Napoli", page_icon=":cityscape:")
    local_css("frontend/style.css")

    st.session_state['logged_in'] = st.session_state.get('logged_in', False) # Inizializza logged_in a False se non esiste
    st.session_state['form_data'] = None # **INIZIALIZZA form_data a None QUI!**


    # --- SIDEBAR MENU ---
    st.sidebar.image("frontend/images/logo_comune_di_napoli.png", width=120) # Immagine LOCALE logo
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

    dipendente_foto_path = "frontend/images/dipendente_foto.png" # Immagine LOCALE
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