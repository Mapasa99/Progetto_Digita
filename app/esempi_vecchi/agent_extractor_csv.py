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
from services.pdf_processor import extract_text_from_pdf
from dotenv import load_dotenv

# Debug: Stampiamo un messaggio per verificare che il file sia stato avviato
print("🚀 Avvio dell'Agente AI...")
load_dotenv()

def get_llm():
    """ Configura e inizializza il modello Claude 3 Haiku su Amazon Bedrock """
    print("📌 Inizializzazione di Bedrock...")  # Debug

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
   #print(os.getenv('AWS_ACCESS_KEY_ID'))
    print("✅ Client Amazon Bedrock inizializzato correttamente!")  # Debug

    return ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        client=bedrock_client,
        model_kwargs={"temperature": 0, "max_tokens": 4000}
    )

# Inizializza il modello AI
model = get_llm()

PROMPT_TEMPLATE = """Estrai una lista di progetti di sucesso, dove per ognuno devi estrarre i seguenti parametri dal testo del documento:
- Nome del progetto
- Città
- Nazione
- Anno
- Superficie (m2)
- Tipologia
- Problema
- Interventi
- Costo totale
- Fonte di finanziamento
- Benefici sociali
- Benefici economici
- Sostenibilità

Restituisci i dati in formato JSON coma una lista di dizioanri con queste chiavi: 
[nome, città, nazione, anno, superficie, tipologia, problema, interventi, costo_totale, fonte_finanziamento, benefici_sociali, benefici_economici, sostenibilita].

Testo del documento:
{text}
Ritorna solo il json senza nessun'altra parola
"""

def extract_json_from_text(text):
    """ Estrae il JSON puro dalla risposta di Bedrock """
    if not isinstance(text, str):  # ✅ Controllo per evitare errori
        print("❌ ERRORE: Il testo ricevuto non è una stringa!")
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)  # Cerca un blocco JSON
    return match.group(0) if match else None

def analyze_pdf(pdf_path):
    """ Estrae e struttura i dati di un PDF usando Claude 3 Haiku """
    print("📌 Inizio analisi del PDF:", pdf_path)  # Debug

    # Verifica se il file esiste
    if not os.path.exists(pdf_path):
        print("❌ ERRORE: Il file PDF non esiste:", pdf_path)
        return None

    extracted_text = extract_text_from_pdf(pdf_path)
    print("📌 Testo estratto (primi 500 caratteri):", extracted_text[:500])  # Debug

    prompt = PROMPT_TEMPLATE.format(text=extracted_text)
    print("📌 Prompt inviato al modello AI...")  # Debug

    response = model.invoke(prompt)  # Correzione: usare invoke() invece di predict()
    print("📌 Risposta ricevuta dal modello:\n", response)

    # ✅ Estrarre il contenuto testuale dall'oggetto AIMessage
    response_text = response.content if hasattr(response, "content") else str(response)

    json_text = extract_json_from_text(response_text)  # Ora passiamo una stringa pura

    if json_text is None:
        print("❌ ERRORE: Nessun JSON trovato nella risposta AI!")
        return None

    try:
        extracted_data = json.loads(json_text)  # ✅ Ora la conversione JSON dovrebbe funzionare
        print("✅ JSON convertito correttamente!")
    except json.JSONDecodeError:
        print("❌ ERRORE: Problema nella conversione del JSON!\n📌 Risposta pulita:\n", json_text)
        return None
    

    return extracted_data


def save_to_csv(data, output_file="data/progetti_successo.csv"):
    """ Salva i dati estratti in un file CSV strutturato """
    print("📌 Salvataggio dei dati su CSV...")  # Debug
    df = pd.DataFrame([data])

    if os.path.exists(output_file):
        df_existing = pd.read_csv(output_file)
        df = pd.concat([df_existing, df], ignore_index=True)

    df.to_csv(output_file, index=False)
    print(f"✅ Dati salvati in {output_file}")  # Debug

# 📌 Avvio dell'analisi se il file viene eseguito direttamente
if __name__ == "__main__":
    print("📌 Esecuzione principale...")  # Debug
    pdf_path = "data/nuovi_progetti/progetto.pdf"

    extracted_data = analyze_pdf(pdf_path)

    if extracted_data:
        save_to_csv(extracted_data)
        print("✅ Analisi completata e dati salvati!")
    else:
        print("❌ ERRORE: Nessun dato estratto.")