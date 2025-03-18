import sqlite3
import pandas as pd
import os

# 📌 Percorsi dei file
csv_file = "progetti_DB.csv"  # Assicurati che il file sia nella stessa cartella dello script
db_file = "progetti_DB.sqlite"  # Nome del database SQLite

def crea_database():
    """ Crea il database e la tabella progetti_successo se non esistono """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Creiamo la tabella nel database
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
            costo_milioni REAL,
            finanziamento TEXT,
            benefici_sociali TEXT,
            benefici_economici TEXT,
            sostenibilita TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database e tabella creati con successo!")

def inserisci_dati():
    """ Inserisce i dati dal file CSV nel database SQLite """
    if not os.path.exists(csv_file):
        print(f"❌ ERRORE: Il file CSV '{csv_file}' non esiste!")
        return

    # 📌 Carica il CSV (modifica il separatore se necessario)
    df = pd.read_csv(csv_file, sep=";")  # Cambia `sep=","` se il separatore è diverso

    # 📌 Connessione al database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 📌 Inseriamo i dati evitando duplicati (basandoci sul nome del progetto)
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO progetti_successo (
                    nome, citta, paese, anno, superficie_mq, tipologia, problema, interventi,
                    costo_milioni, finanziamento, benefici_sociali, benefici_economici, sostenibilita
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["nome"], row["citta"], row["paese"], row["anno"],
                row["superficie_mq"], row["tipologia"], row["problema"], row["interventi"],
                row["costo_milioni"], row["finanziamento"], row["benefici_sociali"],
                row["benefici_economici"], row["sostenibilita"]
            ))
        except sqlite3.IntegrityError:
            print(f"⚠️ Il progetto '{row['nome']}' esiste già nel database. Ignorato.")

    conn.commit()
    conn.close()
    print("✅ Dati inseriti nel database!")

# 📌 Esegui il codice
if __name__ == "__main__":
    crea_database()
    inserisci_dati()
    print("🎯 Database pronto con i dati caricati!")
