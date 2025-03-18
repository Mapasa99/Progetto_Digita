import os
import pickle
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords

# Scaricare le stopwords se necessario
nltk.download('stopwords')
stop_words = set(stopwords.words('italian'))

# 📌 Percorsi dei file
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_PATH = os.path.join(BASE_DIR, "Progetto_DB", "progetti_DB.sqlite")
PICKLE_VECTORIZER = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")
PICKLE_MATRIX = os.path.join(BASE_DIR, "tfidf_matrix.pkl")

def carica_progetti():
    """ Carica i dati dal database SQLite """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM progetti_successo", conn)
    conn.close()
    return df

def preprocess_text(text):
    """ Pulisce e normalizza il testo rimuovendo stopwords e caratteri speciali """
    if not isinstance(text, str):
        return ""
    tokens = text.lower().split()
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return " ".join(filtered_tokens)

# 📌 Pesi personalizzati per i campi testuali (escludendo quelli numerici)
TEXT_WEIGHTS = {
    "problema": 3.0,  
    "interventi": 2.5,  
    "tipologia": 2.0,  
    "benefici_sociali": 1.5,  
    "benefici_economici": 1.5,  
    "nome": 1.0,  
    "sostenibilita": 1.0,  
    "citta": 0.5,  
    "paese": 0.5  
}

df = carica_progetti()

if df.empty:
    print("❌ ERRORE: Il database è vuoto!")
else:
    print("✅ Database caricato! Creazione della colonna `testo_completo`...")

    # Creazione della colonna 'testo_completo' con pesi personalizzati
    df['testo_completo'] = df.apply(lambda row: " ".join([
        (str(row[col]) + " ") * int(TEXT_WEIGHTS[col]) if col in TEXT_WEIGHTS else ""
        for col in TEXT_WEIGHTS.keys()
    ]), axis=1)

    # Pulizia del testo
    df['testo_completo'] = df['testo_completo'].apply(preprocess_text)

    print("✅ Creazione della colonna `testo_completo` completata!")

    # Creazione e salvataggio del modello TF-IDF
    print("📌 Creazione del modello TF-IDF...")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['testo_completo'])

    with open(PICKLE_VECTORIZER, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(PICKLE_MATRIX, "wb") as f:
        pickle.dump(tfidf_matrix, f)

    print("✅ Modello TF-IDF e embedding salvati con successo!")


