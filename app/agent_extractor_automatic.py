# import os
# import json
# import sqlite3
# import pdfplumber
# import boto3
# from botocore.config import Config
# from langchain_aws import ChatBedrock

# DB_PATH = "app/Progetto_DB/progetti_DB.sqlite"

# # 📌 Configurazione Amazon Bedrock
# bedrock_client = boto3.client(
#     service_name='bedrock-runtime',
#     region_name='eu-west-1',
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     verify=False,
#     config=Config(proxies={'https': None})
# )

# model = ChatBedrock(
#     model_id="anthropic.claude-3-haiku-20240307-v1:0",
#     client=bedrock_client,
#     model_kwargs={"temperature": 0, "max_tokens": 4000}
# )

# def analyze_pdf_and_save(pdf_path):
#     """Analizza il PDF e salva i dati nel database"""
#     if not os.path.exists(pdf_path):
#         print(f"❌ Errore: Il file '{pdf_path}' non esiste.")
#         return

#     print(f"📌 Analizzando il file: {pdf_path}")

#     with pdfplumber.open(pdf_path) as pdf:
#         extracted_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

#     prompt = f"""
#     Estrai dati in formato JSON dal seguente testo:
#     {extracted_text}
#     """
    
#     response = model.invoke(prompt)
#     extracted_data = json.loads(response.content if hasattr(response, "content") else str(response))

#     # 📌 Salva i dati nel database SQLite
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS progetti_successo (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nome TEXT UNIQUE,
#             citta TEXT,
#             paese TEXT,
#             anno INTEGER,
#             superficie_mq INTEGER,
#             tipologia TEXT,
#             problema TEXT,
#             interventi TEXT,
#             costo_milioni TEXT,
#             finanziamento TEXT,
#             benefici_sociali TEXT,
#             benefici_economici TEXT,
#             sostenibilita TEXT
#         )
#     """)

#     for progetto in extracted_data:
#         try:
#             cursor.execute("""
#                 INSERT INTO progetti_successo (
#                     nome, citta, paese, anno, superficie_mq, tipologia, problema, interventi, 
#                     costo_milioni, finanziamento, benefici_sociali, benefici_economici, sostenibilita
#                 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 progetto["nome"], progetto["citta"], progetto["paese"], progetto["anno"],
#                 progetto["superficie_mq"], progetto["tipologia"], progetto["problema"], progetto["interventi"],
#                 progetto["costo_milioni"], progetto["finanziamento"], progetto["benefici_sociali"],
#                 progetto["benefici_economici"], progetto["sostenibilita"]
#             ))
#         except sqlite3.IntegrityError:
#             print(f"⚠️ Il progetto '{progetto['nome']}' esiste già nel database. Ignorato.")

#     conn.commit()
#     conn.close()
#     print("✅ Dati salvati nel database con successo!")

import os
import json
import sqlite3
import unicodedata
import re
import urllib3
import boto3
from botocore.config import Config
from langchain_aws import ChatBedrock
from dotenv import load_dotenv
from app.pdf_processor import extract_text_from_pdf

# 🔹 Carica variabili d'ambiente
load_dotenv()

# 🔹 Percorso del database SQLite
DB_PATH = r"app/Progetto_DB/progetti_DB.sqlite"

# 🔹 Disattiva i warning SSL per Bedrock
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_llm():
    """ Configura e inizializza il modello Claude 3 Haiku su Amazon Bedrock """
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='eu-west-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        verify=False,
        config=Config(proxies={'https': None})
    )
    return ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        client=bedrock_client,
        model_kwargs={"temperature": 0, "max_tokens": 4000}
    )

# 🔹 Inizializza il modello AI (Claude 3 Haiku)
model = get_llm()

PROMPT_TEMPLATE = """Estrai una lista di progetti di successo, dove per ognuno devi estrarre i seguenti parametri dal testo del documento:
- Nome 
- Città
- Paese
- Anno
- Superficie_mq
- Tipologia
- Problema
- Interventi
- Costo_milioni
- Finanziamento
- Benefici_sociali
- Benefici_economici
- Sostenibilità

Restituisci i dati in formato JSON come una lista di dizionari con queste chiavi: 
[nome, citta, paese, anno, superficie_mq, tipologia, problema, interventi, costo_milioni, finanziamento, benefici_sociali, benefici_economici, sostenibilita].

Testo del documento:
{text}
Ritorna solo il JSON senza nessun'altra parola.
"""

def extract_json_from_text(text):
    """ Estrae il JSON puro dalla risposta di Bedrock """
    if not isinstance(text, str):  
        return None

    match = re.search(r"\[.*\]", text, re.DOTALL)
    json_text = match.group(0) if match else text  

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None

def analyze_pdf(pdf_path):
    """ Estrae e struttura i dati di un PDF usando Claude 3 Haiku """
    print(f"📌 Inizio analisi del PDF: {pdf_path}")

    if not os.path.exists(pdf_path):
        print(f"❌ ERRORE: Il file PDF non esiste: {pdf_path}")
        return None

    print("📌 Tentativo di estrarre il testo dal PDF...")
    
    try:
        extracted_text = extract_text_from_pdf(pdf_path)
        print("✅ Testo estratto correttamente!")  # ✅ Questa riga dovrebbe essere stampata se la funzione funziona
    except Exception as e:
        print(f"❌ ERRORE: Problema nell'estrazione del testo: {str(e)}")
        return None

    print(f"📌 Testo estratto (primi 500 caratteri):\n{extracted_text[:500]}")  # ✅ Controllo il contenuto del testo

    if not extracted_text.strip():
        print("❌ ERRORE: Il PDF non contiene testo leggibile!")
        return None

    prompt = PROMPT_TEMPLATE.format(text=extracted_text)
    response = model.invoke(prompt)
    
    response_text = response.content if hasattr(response, "content") else str(response)
    json_data = extract_json_from_text(response_text)

    return json_data


def normalize_json_keys(data):
    """ Normalizza le chiavi del JSON rimuovendo accenti e caratteri speciali """
    return [
        {unicodedata.normalize('NFKD', k).encode('ASCII', 'ignore').decode(): v for k, v in progetto.items()}
        for progetto in data
    ]

# def save_to_db(data, db_path=DB_PATH):
#     """ Salva i dati estratti in un database SQLite """
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS progetti_successo (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nome TEXT UNIQUE,
#             citta TEXT,
#             paese TEXT,
#             anno INTEGER,
#             superficie_mq INTEGER,
#             tipologia TEXT,
#             problema TEXT,
#             interventi TEXT,
#             costo_milioni TEXT,
#             finanziamento TEXT,
#             benefici_sociali TEXT,
#             benefici_economici TEXT,
#             sostenibilita TEXT
#         )
#     """)

#     data = normalize_json_keys(data)

#     for progetto in data:
#         try:
#             cursor.execute("""
#                 INSERT INTO progetti_successo (
#                     nome, citta, paese, anno, superficie_mq, tipologia, problema, interventi, 
#                     costo_milioni, finanziamento, benefici_sociali, benefici_economici, sostenibilita
#                 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 progetto["nome"], progetto["citta"], progetto["paese"], progetto["anno"],
#                 progetto["superficie_mq"], progetto["tipologia"], progetto["problema"], progetto["interventi"],
#                 progetto["costo_milioni"], progetto["finanziamento"], progetto["benefici_sociali"],
#                 progetto["benefici_economici"], progetto["sostenibilita"]
#             ))

#         except sqlite3.IntegrityError:
#             print(f"⚠️ Il progetto '{progetto['nome']}' esiste già nel database. Ignorato.")

#     conn.commit()
#     conn.close()

# import os
# import sqlite3

# def save_to_db(data, db_path=DB_PATH):
#     """ Salva i dati estratti in un database SQLite """
#     absolute_path = os.path.abspath(db_path)  # Ottieni il percorso assoluto
#     print(f"📌 Verifica percorso DB: {absolute_path}")

#     if not os.path.exists(os.path.dirname(absolute_path)):
#         print(f"❌ ERRORE: La cartella del database non esiste -> {os.path.dirname(absolute_path)}")
#         return {"error": "❌ La cartella del database non esiste."}

#     try:
#         conn = sqlite3.connect(absolute_path)
#         print("✅ Database aperto con successo!")
#     except sqlite3.Error as e:
#         print(f"❌ ERRORE: Non posso aprire il database: {str(e)}")
#         return {"error": f"❌ Problema nell'aprire il database: {str(e)}"}

#     cursor = conn.cursor()
    
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS progetti_successo (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nome TEXT UNIQUE,
#             citta TEXT,
#             paese TEXT,
#             anno INTEGER,
#             superficie_mq INTEGER,
#             tipologia TEXT,
#             problema TEXT,
#             interventi TEXT,
#             costo_milioni TEXT,
#             finanziamento TEXT,
#             benefici_sociali TEXT,
#             benefici_economici TEXT,
#             sostenibilita TEXT
#         )
#     """)

#     conn.commit()
#     conn.close()
#     print("✅ Dati salvati nel database!")


# def save_to_db(data, db_path=DB_PATH):
#     """ Salva i dati nel database SQLite, evitando duplicati """
#     absolute_path = os.path.abspath(db_path)
#     db_folder = os.path.dirname(absolute_path)

#     if not os.path.exists(db_folder):
#         os.makedirs(db_folder, exist_ok=True)

#     try:
#         conn = sqlite3.connect(absolute_path)
#         cursor = conn.cursor()
#         print("✅ Database aperto con successo!")
#     except sqlite3.Error as e:
#         print(f"❌ ERRORE: Non posso aprire il database: {str(e)}")
#         return {"error": f"❌ Problema nell'aprire il database: {str(e)}"}

#     # ✅ Crea la tabella se non esiste
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS progetti_successo (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nome TEXT UNIQUE,
#             citta TEXT,
#             paese TEXT,
#             anno INTEGER,
#             superficie_mq INTEGER,
#             tipologia TEXT,
#             problema TEXT,
#             interventi TEXT,
#             costo_milioni TEXT,
#             finanziamento TEXT,
#             benefici_sociali TEXT,
#             benefici_economici TEXT,
#             sostenibilita TEXT
#         )
#     """)

#     conn.commit()

#     data = normalize_json_keys(data)

#     for progetto in data:
#         # ✅ Controlliamo se il progetto è già presente nel database
#         cursor.execute("SELECT COUNT(*) FROM progetti_successo WHERE nome = ?", (progetto["nome"],))
#         result = cursor.fetchone()

#         if result[0] > 0:
#             print(f"⚠️ Il progetto '{progetto['nome']}' esiste già. NON verrà inserito.")
#             continue  # Salta l'inserimento se il progetto è già presente

#         try:
#             print(f"📌 Inserisco il progetto '{progetto['nome']}' nel database...")
#             cursor.execute("""
#                 INSERT INTO progetti_successo (
#                     nome, citta, paese, anno, superficie_mq, tipologia, problema, interventi, 
#                     costo_milioni, finanziamento, benefici_sociali, benefici_economici, sostenibilita
#                 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 progetto["nome"], progetto["citta"], progetto["paese"], progetto["anno"],
#                 progetto["superficie_mq"], progetto["tipologia"], progetto["problema"], progetto["interventi"],
#                 progetto["costo_milioni"], progetto["finanziamento"], progetto["benefici_sociali"],
#                 progetto["benefici_economici"], progetto["sostenibilita"]
#             ))

#         except sqlite3.IntegrityError as e:
#             print(f"❌ ERRORE SQL: {e}")

#     conn.commit()
#     conn.close()
#     print("✅ Dati aggiornati nel database!")
#     return {"message": "✅ Dati aggiornati nel database!"}

def save_to_db(data, db_path=DB_PATH):
    """ Salva i dati nel database SQLite, evitando duplicati e trasformando liste in stringhe. """
    absolute_path = os.path.abspath(db_path)
    db_folder = os.path.dirname(absolute_path)

    if not os.path.exists(db_folder):
        os.makedirs(db_folder, exist_ok=True)

    try:
        conn = sqlite3.connect(absolute_path)
        cursor = conn.cursor()
        print("✅ Database aperto con successo!")
    except sqlite3.Error as e:
        print(f"❌ ERRORE: Non posso aprire il database: {str(e)}")
        return {"error": f"❌ Problema nell'aprire il database: {str(e)}"}

    # ✅ Creazione tabella
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progetti_successo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            citta TEXT,
            paese TEXT,
            anno INTEGER,
            superficie_mq INTEGER,
            tipologia TEXT,
            problema TEXT,
            interventi TEXT,  -- Questo è il parametro 8 che stava dando errore
            costo_milioni REAL,
            finanziamento TEXT,
            benefici_sociali TEXT,
            benefici_economici TEXT,
            sostenibilita TEXT
        )
    """)

    conn.commit()

    data = normalize_json_keys(data)

    for progetto in data:
        # ✅ Convertiamo ogni lista in stringa JSON
        for key, value in progetto.items():
            if isinstance(value, list):  # Se il valore è una lista
                progetto[key] = json.dumps(value)  # Converti in stringa JSON

        # ✅ Controllo se il progetto esiste già
        cursor.execute("SELECT COUNT(*) FROM progetti_successo WHERE nome = ?", (progetto["nome"],))
        result = cursor.fetchone()

        if result[0] > 0:
            print(f"⚠️ Il progetto '{progetto['nome']}' esiste già. NON verrà inserito.")
            continue

        try:
            print(f"📌 Inserisco il progetto '{progetto['nome']}' nel database...")
            cursor.execute("""
                INSERT INTO progetti_successo (
                    nome, citta, paese, anno, superficie_mq, tipologia, problema, interventi, 
                    costo_milioni, finanziamento, benefici_sociali, benefici_economici, sostenibilita
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                progetto["nome"], progetto["citta"], progetto["paese"], progetto["anno"],
                progetto["superficie_mq"], progetto["tipologia"], progetto["problema"], progetto["interventi"],
                progetto["costo_milioni"], progetto["finanziamento"], progetto["benefici_sociali"],
                progetto["benefici_economici"], progetto["sostenibilita"]
            ))

        except sqlite3.IntegrityError as e:
            print(f"❌ ERRORE SQL: {e}")

    conn.commit()
    conn.close()
    print("✅ Dati aggiornati nel database!")


def process_pdf_and_save(pdf_path):
    """
    Funzione principale che analizza il PDF e salva i dati nel database.
    Questa funzione viene chiamata direttamente dal backend FastAPI.
    """
    print(f"📌 Inizio analisi PDF: {pdf_path}")

    if not os.path.exists(pdf_path):
        print(f"❌ ERRORE: Il file non esiste -> {pdf_path}")
        return {"error": "❌ Il file PDF non esiste."}

    extracted_data = analyze_pdf(pdf_path)

    if extracted_data:
        print(f"✅ Dati estratti: {extracted_data}")  # ✅ Debug JSON estratto
        save_to_db(extracted_data)
        return {"message": "✅ Analisi completata e dati salvati nel database!", "data": extracted_data}
    else:
        print("❌ ERRORE: Nessun dato estratto dal PDF.")
        return {"error": "❌ Nessun dato estratto dal PDF."}

