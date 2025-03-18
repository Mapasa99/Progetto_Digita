import os
import json
import pandas as pd
import boto3
import urllib3
import matplotlib.pyplot as plt
from botocore.config import Config
from langchain_aws import ChatBedrock
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from dotenv import load_dotenv

# 📌 Carichiamo le variabili d'ambiente
load_dotenv()

# 📌 Percorsi dei file
CSV_PATH = "risultati.csv"
PDF_PATH = "report_riqualificazione.pdf"
GRAPH_COSTS_PATH = "grafico_costi.png"
JSON_OUTPUT_PATH = "risultati.json"

# 📌 Configurazione del modello Claude 3 Haiku su Amazon Bedrock
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

# 📌 Inizializziamo il modello AI
model = get_llm()

# 📌 Funzione per leggere i dati dal CSV e convertirli in JSON
def leggi_risultati():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"❌ ERRORE: Il file '{CSV_PATH}' non esiste!")
    
    df = pd.read_csv(CSV_PATH)
    if df.empty:
        raise ValueError("❌ ERRORE: Il file CSV è vuoto!")
    
    progetti_json = df.to_dict(orient="records")
    
    # 📌 Salva il JSON su file per debug
    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as json_file:
        json.dump(progetti_json, json_file, indent=4, ensure_ascii=False)
    
    print("📌 JSON generato dal CSV salvato con successo.", progetti_json)
    return df, progetti_json

# 📌 Genera il report AI con Claude
def genera_documento_ai(progetti_json):
    prompt = f"""
    Sei un esperto di riqualificazione urbana. Ho ottenuto 5 progetti simili tramite un modello ML.

    📌 Progetti di successo trovati:  
    {json.dumps(progetti_json, indent=4)}

     Obiettivo: 
    - Analizza i punti di forza e le debolezze di ciascun progetto  
    - Confronta i progetti in termini di costi, sostenibilità ed efficacia 
    - Suggerisci strategie ottimali per il nuovo progetto 

    Formato richiesto per il Report:
    1 Introduzione: Contesto della riqualificazione e obiettivi  
    2 Analisi Comparativa:  
    - **Tabella dettagliata con confronto costi, impatto e sostenibilità** (da includere nel report)  
    - **Inserire il grafico generato automaticamente per visualizzare i costi dei progetti**  
    - Identifica elementi di successo e criticità di ogni progetto  
    3 Strategie Consigliate:
    - 3 soluzioni concrete per migliorare la riqualificazione  
    - Include riferimenti specifici ai progetti più efficaci  
    4 Conclusione:  
    - Sintesi delle migliori pratiche  
    - Suggerimenti pratici basati sui 5 progetti simili  
    """
    
    print("📌 Invio del prompt a Claude 3 Haiku...")
    response = model.invoke(prompt)
    documento_ai = response.content if hasattr(response, "content") else str(response)

    return documento_ai

# 📌 Funzione per generare i grafici di confronto
def genera_grafici(df):
    plt.figure(figsize=(8, 5))
    plt.bar(df["nome"], df["costo_milioni"], color="blue")
    plt.xlabel("Progetti")
    plt.ylabel("Costo (milioni €)")
    plt.title("Confronto Costi dei Progetti")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(GRAPH_COSTS_PATH)
    plt.close()
    print("📊 Grafico dei costi salvato.")

# 📌 Funzione per generare la tabella nel PDF
def crea_tabella_pdf(progetti_json):
    headers = list(progetti_json[0].keys())
    table_data = [headers] + [[item[header] for header in headers] for item in progetti_json]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    return table

# 📌 Funzione per generare il PDF con testo AI, tabella e grafico
def salva_report_pdf(contenuto_testo, progetti_json):
    print("📌 Creazione del nuovo PDF...")
    doc = SimpleDocTemplate(PDF_PATH, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()

    stile_titolo = ParagraphStyle('Titolo', parent=styles['Heading1'], fontSize=22, textColor=colors.darkblue, spaceAfter=20)
    stile_testo = ParagraphStyle('Testo', parent=styles['BodyText'], fontSize=12, leading=14, spaceAfter=10)

    elementi = [Paragraph("REPORT DI RIQUALIFICAZIONE URBANA", stile_titolo), Spacer(1, 12)]
    sezioni = contenuto_testo.split("\n\n")
    for sezione in sezioni:
        elementi.append(Paragraph(sezione.strip(), stile_testo))
        elementi.append(Spacer(1, 12))
    
    elementi.append(crea_tabella_pdf(progetti_json))
    elementi.append(Spacer(1, 20))
    
    # 📌 Aggiunta del grafico nel PDF
    if os.path.exists(GRAPH_COSTS_PATH):
        elementi.append(Image(GRAPH_COSTS_PATH, width=400, height=300))
        elementi.append(Spacer(1, 20))
    
    doc.build(elementi)
    print(f"✅ Report salvato: {PDF_PATH}")

# 📌 Esegui il report
if __name__ == "__main__":
    try:
        print("📌 Avvio del processo...")
        df_progetti, progetti_json = leggi_risultati()
        genera_grafici(df_progetti)
        contenuto_ai = genera_documento_ai(progetti_json)
        salva_report_pdf(contenuto_ai, progetti_json)
        print("✅ Processo completato con successo!")
    except Exception as e:
        print(f"❌ Errore durante l'esecuzione: {e}")
