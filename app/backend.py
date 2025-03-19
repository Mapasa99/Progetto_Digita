# from fastapi import FastAPI, UploadFile, File
# import os
# import shutil
# import subprocess


# app = FastAPI()

# UPLOAD_FOLDER = "./uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# AGENT_SCRIPT = "./agent_extractor_automatic.py"  # Percorso corretto del file

# @app.post("/upload_pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     """Riceve un PDF, lo salva e avvia l'agente AI per analizzarlo"""
    
#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)

#     # 📌 Salva il file nella cartella specificata
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     print("<<<File salvato>>>", file_path)
#     # 📌 Avvia l'agente per analizzare il file
#     try:
#         result = subprocess.run(["python", AGENT_SCRIPT, file_path], check=True, capture_output=True, text=True)
#         print("<<<Result>>>", result)
#         return {"message": f"✅ PDF salvato e analizzato con successo: {file.filename}"}
#     except subprocess.CalledProcessError as e:
#         print('mica sto andando in eccezion?')
#         return {"error": f"❌ Errore durante l'analisi del PDF: {e.stderr}"}

# from fastapi import FastAPI, UploadFile, File
# import os
# import shutil

# # ✅ Importa direttamente la funzione dall'agent
# from app.agent_extractor_automatic import analyze_pdf_and_save

# app = FastAPI()

# UPLOAD_FOLDER = "./uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.post("/upload_pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     """Riceve un PDF, lo salva e avvia l'agente AI per analizzarlo direttamente"""

#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)

#     # 📌 Salva il file nella cartella specificata
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     print("<<<File salvato>>>", file_path)

#     # 📌 Chiamata diretta alla funzione di analisi senza subprocess
#     try:
#         analyze_pdf_and_save(file_path)
#         return {"message": f"✅ PDF salvato e analizzato con successo: {file.filename}"}
#     except Exception as e:
#         return {"error": f"❌ Errore durante l'analisi del PDF: {str(e)}"}

# from fastapi import FastAPI, UploadFile, File
# import os
# import shutil
# from app.agent_extractor_automatic import process_pdf_and_save

# app = FastAPI()

# UPLOAD_FOLDER = "./uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.post("/upload_pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     """Riceve un PDF, lo salva e avvia l'agente AI per analizzarlo direttamente"""

#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)

#     # 📌 Salva il file nella cartella specificata
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     print("<<< File salvato >>>", file_path)

#     # 📌 Chiamata diretta alla funzione di analisi
#     result = process_pdf_and_save(file_path)
    
#     return result

from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil
from app.agent_extractor_automatic import process_pdf_and_save  # ✅ Import corretto
import sqlite3  # ✅ Import necessario per gestire il database SQLite
from pydantic import BaseModel
from app.ml_similarity import carica_progetti, calcola_similarita

app = FastAPI()

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Riceve un PDF, lo salva e avvia l'agente AI per analizzarlo direttamente"""

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    # ✅ Debug: Stampa il percorso del file
    print(f"📌 Percorso file salvato: {file_path}")

    try:
        # 📌 Salva il file nella cartella specificata
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print("✅ File salvato con successo!")

        # 📌 Chiamata alla funzione di analisi
        result = process_pdf_and_save(file_path)
        print(f"📌 Risultato analisi: {result}")

        return result

    except Exception as e:
        print(f"❌ Errore durante l'analisi: {e}")
        return {"error": f"❌ Errore durante l'analisi del PDF: {str(e)}"}

DB_PATH = "app/Progetto_DB/progetti_DB.sqlite"  # Assicurati che il percorso sia corretto


@app.get("/latest_projects/")
def get_latest_projects():
    """Restituisce le ultime 5 righe del database"""
    absolute_path = os.path.abspath(DB_PATH)

    if not os.path.exists(absolute_path):
        return {"error": "❌ Il database non esiste."}

    try:
        conn = sqlite3.connect(absolute_path)
        cursor = conn.cursor()

        # ✅ Prende le ultime 5 righe ordinate per ID (le più recenti)
        cursor.execute("SELECT * FROM progetti_successo ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()

        # ✅ Recuperiamo i nomi delle colonne
        columns = [desc[0] for desc in cursor.description]

        conn.close()

        # ✅ Convertiamo in formato JSON
        latest_projects = [dict(zip(columns, row)) for row in rows]
        return {"latest_projects": latest_projects}

    except sqlite3.Error as e:
        return {"error": f"❌ Errore nel database: {str(e)}"}
    

# 📌 Modello dei dati in ingresso
class ProjectInput(BaseModel):
    problema: str
    interventi: str
    tipologia: str
    benefici_sociali: str
    benefici_economici: str
    nome: str
    sostenibilita: str
    citta: str
    paese: str
    superficie_mq: float
    costo_milioni: float

@app.post("/match_project/")
def match_project(project: ProjectInput):
    """ Riceve i dati del progetto e restituisce i più simili dal database """
    risultati = calcola_similarita(project)
    
    if not risultati:
        raise HTTPException(status_code=404, detail="Nessun progetto trovato.")

    return {"progetti_simili": risultati}
