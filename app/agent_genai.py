#AGENT GEN AI

import os
import json
import pandas as pd
import boto3
import urllib3
import matplotlib.pyplot as plt
import numpy as np
from botocore.config import Config
from langchain_aws import ChatBedrock
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from dotenv import load_dotenv

# 📌 Carichiamo le variabili d'ambiente
load_dotenv()

# 📌 Percorsi dei file
PDF_PATH = "app/report_riqualificazione.pdf"
GRAPH_COSTS_PATH = "grafico_costi.png"
GRAPH_SUSTAINABILITY_PATH = "grafico_sostenibilita.png"


# 📌 Configurazione Bedrock
def get_llm():
    print("📌 Inizializzazione di Bedrock...")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='eu-west-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        verify=False,
        config=Config(proxies={'https': None})
    )

    print("✅ Client Amazon Bedrock inizializzato correttamente!")
    return ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        client=bedrock_client,
        model_kwargs={"temperature": 0.3, "max_tokens": 4000}
    )


# # 📌 Funzione per generare il report
# def generate_report(progetti_json):
#     """Genera un report PDF basato sui 5 progetti migliori"""

#     print("🚀 Avvio della generazione del report...")

#     # 📌 Modello AI per generare il testo
#     model = get_llm()

#     # 📌 Prepara il prompt
#     prompt = f"""
#     Sei un esperto di riqualificazione urbana. Genera un report dettagliato basato sui seguenti 5 progetti:
#     {json.dumps(progetti_json, indent=4)}
#     Il report deve includere:
#     1. Executive Summary
#     2. Introduzione
#     3. Analisi dettagliata dei progetti
#     4. Confronto tra i progetti
#     5. Strategie ottimali
#     6. Conclusioni
#     """
    
#     print("📌 Generazione del testo con AI...")
#     response = model.invoke(prompt)
#     contenuto_ai = response.content if hasattr(response, "content") else str(response)

#     print("✅ Testo AI generato!")

#     # 📌 Creazione del report PDF
#     doc = SimpleDocTemplate(PDF_PATH, pagesize=letter)
#     styles = getSampleStyleSheet()

#     elementi = [Paragraph("REPORT DI RIQUALIFICAZIONE URBANA", styles['Title']), Spacer(1, 12)]

#     for sezione in contenuto_ai.split("\n\n"):
#         elementi.append(Paragraph(sezione, styles['BodyText']))
#         elementi.append(Spacer(1, 12))

#     doc.build(elementi)

#     print(f"✅ Report PDF salvato: {PDF_PATH}")
#     return PDF_PATH

def generate_report(progetti_json):
    """Genera un report PDF basato sui 5 progetti migliori"""

    print("🚀 Avvio della generazione del report...")

    # 📌 Modello AI per generare il testo
    print("📌 Creazione client Bedrock...")
    model = get_llm()

    # 📌 Prepara il prompt
    prompt = f"""
    Sei un esperto di riqualificazione urbana. Genera un report dettagliato basato sui seguenti 5 progetti:
    {json.dumps(progetti_json, indent=4)}
    Il report deve includere:
    1. Executive Summary
    2. Introduzione
    3. Analisi dettagliata dei progetti
    4. Confronto tra i progetti
    5. Strategie ottimali
    6. Conclusioni
    """

    print("📌 Prompt generato con successo! Ecco il primo pezzo del prompt:\n", prompt[:500])

    try:
        print("📌 Invio del prompt a Claude 3 Haiku...")
        response = model.invoke(prompt)
        contenuto_ai = response.content if hasattr(response, "content") else str(response)
        print("✅ Testo AI generato!")
    except Exception as e:
        print("❌ ERRORE: Problema con Bedrock AI:", str(e))
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Errore con Amazon Bedrock: {e}")

    # 📌 Creazione del report PDF
    doc = SimpleDocTemplate(PDF_PATH, pagesize=letter)
    styles = getSampleStyleSheet()

    elementi = [Paragraph("REPORT DI RIQUALIFICAZIONE URBANA", styles['Title']), Spacer(1, 12)]

    for sezione in contenuto_ai.split("\n\n"):
        elementi.append(Paragraph(sezione, styles['BodyText']))
        elementi.append(Spacer(1, 12))

    doc.build(elementi)

    print(f"✅ Report PDF salvato: {PDF_PATH}")
    return PDF_PATH