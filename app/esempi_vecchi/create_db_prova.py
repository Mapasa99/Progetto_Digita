import sqlite3
import os

# Creiamo il database localmente nella cartella data/
db_path = "data/progetti_test.db"

# Controlliamo se la cartella "data" esiste, altrimenti la creiamo
if not os.path.exists("data"):
    os.makedirs("data")
    print("📌 Cartella 'data/' creata!")

print("📌 Creazione del database SQLite...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Creiamo la tabella per i progetti di successo
cursor.execute("""
    CREATE TABLE IF NOT EXISTS progetti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        problema TEXT,
        interventi TEXT,
        benefici_sociali TEXT,
        benefici_economici TEXT,
        sostenibilita TEXT
    )
""")
print("✅ Tabella 'progetti' creata o già esistente.")

# Creiamo la tabella per gli spazi da riqualificare
cursor.execute("""
    CREATE TABLE IF NOT EXISTS spazi_riqualificazione (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        problema TEXT,
        interventi TEXT,
        benefici_sociali TEXT,
        benefici_economici TEXT,
        sostenibilita TEXT
    )
""")
print("✅ Tabella 'spazi_riqualificazione' creata o già esistente.")

# Dati di esempio per i progetti di successo
progetti = [
    ("Rinnovo Centro Storico", "Degrado urbano", "Restauro edifici storici, miglioramento viabilità",
     "Aumento turismo, valorizzazione culturale", "Aumento attività commerciali", "Uso materiali eco-sostenibili"),
    
    ("Riqualificazione Quartiere Verde", "Mancanza spazi verdi", "Creazione di parchi e giardini",
     "Miglioramento qualità della vita", "Aumento valore immobiliare", "Uso di piante autoctone, riduzione CO2"),
    
    ("Mobilità Sostenibile", "Traffico congestionato", "Creazione piste ciclabili, miglioramento trasporto pubblico",
     "Miglioramento salute pubblica", "Riduzione costi trasporto", "Riduzione emissioni, incentivi veicoli elettrici"),
    
    ("Edilizia Sociale Innovativa", "Carenza alloggi a prezzi accessibili", "Costruzione nuove abitazioni a basso costo",
     "Inclusione sociale, riduzione povertà", "Creazione posti di lavoro", "Efficienza energetica, materiali riciclati"),
    
    ("Rigenerazione Urbana", "Abbandono aree industriali", "Conversione fabbriche in spazi culturali e commerciali",
     "Rivitalizzazione quartieri", "Nuove opportunità economiche", "Efficientamento energetico, pannelli solari")
]

print("📌 Inserimento dati nella tabella 'progetti'...")
cursor.executemany("""
    INSERT INTO progetti (nome, problema, interventi, benefici_sociali, benefici_economici, sostenibilita)
    VALUES (?, ?, ?, ?, ?, ?)""", progetti)
print("✅ Dati inseriti nella tabella 'progetti'.")

# Dati di esempio per uno spazio da riqualificare
spazio_riqualificare = [
    ("Piazza Centrale", "Spazio pubblico inutilizzato", "Creazione aree pedonali, eventi culturali",
     "Maggiore aggregazione sociale", "Aumento attrattività commerciale", "Uso illuminazione a basso consumo")
]

print("📌 Inserimento dati nella tabella 'spazi_riqualificazione'...")
cursor.executemany("""
    INSERT INTO spazi_riqualificazione (nome, problema, interventi, benefici_sociali, benefici_economici, sostenibilita)
    VALUES (?, ?, ?, ?, ?, ?)""", spazio_riqualificare)
print("✅ Dati inseriti nella tabella 'spazi_riqualificazione'.")

# Salviamo le modifiche e chiudiamo la connessione
conn.commit()
conn.close()

print("✅ Database SQLite 'progetti_test.db' creato con successo in data/")
