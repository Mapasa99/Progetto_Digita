# # BACKEND 
# from fastapi import FastAPI, UploadFile, File, HTTPException
# import os
# import shutil
# import sqlite3  # ✅ Import necessario per gestire il database SQLite
# from typing import List
# from pydantic import BaseModel
# from app.agent_extractor_automatic import process_pdf_and_save  # ✅ Import corretto
# from app.ml_similarity import carica_progetti, calcola_similarita
# from app.agent_genai import generate_report  # ✅ Import corretto

# app = FastAPI()

# UPLOAD_FOLDER = "./uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# DB_PATH = "app/Progetto_DB/progetti_DB.sqlite"  # Assicurati che il percorso sia corretto


# ### **🔹 Endpoint per l'upload di PDF**
# @app.post("/upload_pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     """Riceve un PDF, lo salva e avvia l'agente AI per analizzarlo direttamente"""

#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     print(f"📌 Percorso file salvato: {file_path}")

#     try:
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         print("✅ File salvato con successo!")

#         # 📌 Chiamata all'AI per elaborare il PDF
#         result = process_pdf_and_save(file_path)
#         print(f"📌 Risultato analisi: {result}")

#         return result

#     except Exception as e:
#         print(f"❌ Errore durante l'analisi: {e}")
#         return {"error": f"❌ Errore durante l'analisi del PDF: {str(e)}"}


# ### **🔹 Endpoint per ottenere gli ultimi 5 progetti**
# @app.get("/latest_projects/")
# def get_latest_projects():
#     """Restituisce le ultime 5 righe del database"""
#     absolute_path = os.path.abspath(DB_PATH)

#     if not os.path.exists(absolute_path):
#         return {"error": "❌ Il database non esiste."}

#     try:
#         conn = sqlite3.connect(absolute_path)
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM progetti_successo ORDER BY id DESC LIMIT 5")
#         rows = cursor.fetchall()
#         columns = [desc[0] for desc in cursor.description]
#         conn.close()

#         latest_projects = [dict(zip(columns, row)) for row in rows]
#         return {"latest_projects": latest_projects}

#     except sqlite3.Error as e:
#         return {"error": f"❌ Errore nel database: {str(e)}"}


# ### **🔹 Modello dei dati per la richiesta**
# class ProjectInput(BaseModel):
#     problema: str
#     interventi: str
#     tipologia: str
#     benefici_sociali: str
#     benefici_economici: str
#     nome: str
#     sostenibilita: str
#     citta: str
#     paese: str
#     superficie_mq: float
#     costo_milioni: float


# ### **🔹 Endpoint per trovare i progetti simili**
# @app.post("/match_project/")
# def match_project(project: ProjectInput):
#     """Riceve i dati del progetto e restituisce i più simili dal database"""
#     risultati = calcola_similarita(project)

#     if not risultati:
#         raise HTTPException(status_code=404, detail="Nessun progetto trovato.")

#     return {"progetti_simili": risultati}


# ### **🔹 Modello per la richiesta del report**
# class Progetto(BaseModel):
#     id: int
#     nome: str
#     citta: str
#     paese: str
#     superficie_mq: float
#     costo_milioni: float
#     similarita: float


# class ProgettiRequest(BaseModel):
#     progetti: List[Progetto]  # ✅ Ora accetta il JSON con chiave "progetti"


# ### **🔹 Endpoint per generare il report PDF**
# @app.post("/generate_report/")
# async def generate_report_api(request: ProgettiRequest):
#     """
#     Endpoint che riceve i 5 migliori progetti e genera un report PDF.
#     """
#     try:
#         print("📌 DEBUG: Dati ricevuti per il report:", request.progetti)

#         # ✅ Convertiamo in dizionari per renderlo JSON serializzabile
#         progetti_dict = [progetto.dict() for progetto in request.progetti]
        
#         print("📌 DEBUG: Dati convertiti in dizionari per il report:", progetti_dict)

#         pdf_path = generate_report(progetti_dict)

#         return {"message": "✅ Report generato con successo!", "pdf_path": pdf_path}

#     except Exception as e:
#         print(f"❌ ERRORE durante la generazione del report: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# BACKEND
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
import os
import shutil
import sqlite3  # ✅ Import necessario per gestire il database SQLite
from typing import List
from pydantic import BaseModel
from app.agent_extractor_automatic import process_pdf_and_save  # ✅ Import corretto
from app.ml_similarity import carica_progetti, calcola_similarita
from app.agent_genai import generate_report  # ✅ Import corretto

app = FastAPI()

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = "app/Progetto_DB/progetti_DB.sqlite"  # Assicurati che il percorso sia corretto

### **🔹 Endpoint per l'upload di PDF**
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Riceve un PDF, lo salva e avvia l'agente AI per analizzarlo direttamente"""

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    print(f"📌 Percorso file salvato: {file_path}")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print("✅ File salvato con successo!")

        # 📌 Chiamata all'AI per elaborare il PDF
        result = process_pdf_and_save(file_path)
        print(f"📌 Risultato analisi: {result}")

        return result

    except Exception as e:
        print(f"❌ Errore durante l'analisi: {e}")
        return {"error": f"❌ Errore durante l'analisi del PDF: {str(e)}"}


### **🔹 Endpoint per ottenere gli ultimi 5 progetti**
@app.get("/latest_projects/")
def get_latest_projects():
    """Restituisce le ultime 5 righe del database"""
    absolute_path = os.path.abspath(DB_PATH)

    if not os.path.exists(absolute_path):
        return {"error": "❌ Il database non esiste."}

    try:
        conn = sqlite3.connect(absolute_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM progetti_successo ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        latest_projects = [dict(zip(columns, row)) for row in rows]
        return {"latest_projects": latest_projects}

    except sqlite3.Error as e:
        return {"error": f"❌ Errore nel database: {str(e)}"}


### **🔹 Modello dei dati per la richiesta**
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


### **🔹 Endpoint per trovare i progetti simili**
@app.post("/match_project/")
def match_project(project: ProjectInput):
    """Riceve i dati del progetto e restituisce i più simili dal database"""
    risultati = calcola_similarita(project)

    if not risultati:
        raise HTTPException(status_code=404, detail="Nessun progetto trovato.")

    return {"progetti_simili": risultati}


### **🔹 Modello per la richiesta del report**
class Progetto(BaseModel):
    id: int
    nome: str
    citta: str
    paese: str
    superficie_mq: float
    costo_milioni: float
    similarita: float


class ProgettiRequest(BaseModel):
    progetti: List[Progetto]  # ✅ Ora accetta il JSON con chiave "progetti"


### **🔹 Endpoint per generare il report PDF**
@app.post("/generate_report/")
async def generate_report_api(request: ProgettiRequest):
    """
    Endpoint che riceve i 5 migliori progetti e genera un report PDF.
    """
    try:
        print("📌 DEBUG: Dati ricevuti per il report:", request.progetti)

        # ✅ Convertiamo in dizionari per renderlo JSON serializzabile
        progetti_dict = [progetto.dict() for progetto in request.progetti]

        print("📌 DEBUG: Dati convertiti in dizionari per il report:", progetti_dict)

        pdf_path = generate_report(progetti_dict)

        # 📌 MODIFICA QUI: Leggi il contenuto del PDF e restituiscilo come Response
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        return Response(content=pdf_content, media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=report_riqualificazione.pdf"})

        # ❌ NON RESTITUIRE PIÙ IL PERCORSO DEL FILE
        # return {"message": "✅ Report generato con successo!", "pdf_path": pdf_path}

    except Exception as e:
        print(f"❌ ERRORE durante la generazione del report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))