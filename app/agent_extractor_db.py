import os
import json
import pandas as pd
import sqlite3
import boto3
import urllib3
import re
from botocore.config import Config
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
from pdf_processor import extract_text_from_pdf
from dotenv import load_dotenv
import unicodedata

# Debug: Stampiamo un messaggio per verificare che il file sia stato avviato
print("🚀 Avvio dell'Agente AI...")
load_dotenv()

# 📌 Percorso del database SQLite
DB_PATH = r"Progetto_DB/progetti_DB.sqlite"

def get_llm():
    """ Configura e inizializza il modello Claude 3 Haiku su Amazon Bedrock """
    print("📌 Inizializzazione di Bedrock...")

    # Disabilita avvisi SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Inizializza il client Amazon Bedrock
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='eu-west-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        verify=False,  # Disabilita verifica SSL (solo per test)
        config=Config(proxies={'https': None})
    )

    print("✅ Client Amazon Bedrock inizializzato correttamente!")
    return ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        client=bedrock_client,
        model_kwargs={"temperature": 0, "max_tokens": 4000}
    )

# Inizializza il modello AI
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
        print("❌ ERRORE: Il testo ricevuto non è una stringa!")
        return None

    print("📌 Risposta ricevuta dall'AI (primi 500 caratteri):\n", text[:500])

    # Prova a trovare il JSON puro all'interno del testo
    match = re.search(r"\[.*\]", text, re.DOTALL)

    if match:
        json_text = match.group(0)
        print("📌 JSON Estratto:\n", json_text[:500])
    else:
        json_text = text  # Se non trova il blocco, prova a usare tutto il testo

    try:
        extracted_data = json.loads(json_text)
        print("✅ JSON convertito correttamente!")
        return extracted_data
    except json.JSONDecodeError as e:
        print("❌ ERRORE: Problema nella conversione del JSON!\n📌 Risposta pulita:\n", json_text)
        print("Dettaglio errore JSONDecodeError:", e)
        return None

def analyze_pdf(pdf_path):
    """ Estrae e struttura i dati di un PDF usando Claude 3 Haiku """
    print("📌 Inizio analisi del PDF:", pdf_path)
    if not os.path.exists(pdf_path):
        print("❌ ERRORE: Il file PDF non esiste:", pdf_path)
        return None

    extracted_text = extract_text_from_pdf(pdf_path)
    print("📌 Testo estratto (primi 500 caratteri):", extracted_text[:500])
    prompt = PROMPT_TEMPLATE.format(text=extracted_text)
    print("📌 Prompt inviato al modello AI...")
    response = model.invoke(prompt)
    
    response_text = response.content if hasattr(response, "content") else str(response)
    json_data = extract_json_from_text(response_text)

    if json_data is None:
        print("❌ ERRORE: Nessun JSON trovato nella risposta AI!")
        return None

    return json_data

import unicodedata

def normalize_json_keys(data):
    """ Normalizza le chiavi del JSON rimuovendo accenti e caratteri speciali """
    new_data = []
    for progetto in data:
        progetto_normalizzato = { 
            unicodedata.normalize('NFKD', k).encode('ASCII', 'ignore').decode(): v 
            for k, v in progetto.items()
        }
        new_data.append(progetto_normalizzato)
    return new_data

def save_to_db(data, db_path=DB_PATH):
    """ Salva i dati estratti in un database SQLite """
    print("📌 Salvataggio nel database SQLite...")  
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Creiamo la tabella se non esiste
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
            interventi TEXT,
            costo_milioni TEXT,
            finanziamento TEXT,
            benefici_sociali TEXT,
            benefici_economici TEXT,
            sostenibilita TEXT
        )
    """)

    # ✅ Normalizziamo le chiavi JSON
    data = normalize_json_keys(data)

    for progetto in data:
        try:
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

        except sqlite3.IntegrityError:
            print(f"⚠️ Il progetto '{progetto['nome']}' esiste già nel database. Ignorato.")

    conn.commit()
    conn.close()
    print("✅ Dati salvati nel database!")


if __name__ == "__main__":
    print("📌 Esecuzione principale...")
    pdf_path = r"C:\Users\Mario\Desktop\Progetto_DIGITA\app\data\nuovi_progetti\progetto.pdf"
    extracted_data = analyze_pdf(pdf_path)

    if extracted_data:
        save_to_db(extracted_data)
        print("✅ Analisi completata e dati salvati nel database!")
    else:
        print("❌ ERRORE: Nessun dato estratto.")
