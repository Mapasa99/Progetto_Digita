import os
import pickle
import sqlite3
import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity

# Scarica le stopwords italiane se non presenti
nltk.download('stopwords')
stop_words = set(stopwords.words('italian'))

# 📌 Percorsi aggiornati dei file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Percorso della cartella 'app'
DB_PATH = os.path.join(BASE_DIR, "Progetto_DB", "progetti_DB.sqlite")
VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")
MATRIX_PATH = os.path.join(BASE_DIR, "tfidf_matrix.pkl")
CSV_OUTPUT_PATH = os.path.join(BASE_DIR, "risultati.csv")  # 📌 File CSV output

# 📌 Pesi per i parametri testuali
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

# 📌 Domande chiare per ogni parametro
DOMANDE = {
    "problema": "🔹 Qual è il problema principale che il progetto affronta? (Es: traffico, inquinamento, sicurezza)",
    "interventi": "🔹 Quali interventi sono previsti? (Es: piste ciclabili, illuminazione LED, parchi verdi)",
    "tipologia": "🔹 Qual è la tipologia del progetto? (Es: infrastruttura, mobilità, ambiente, energia)",
    "benefici_sociali": "🔹 Quali benefici sociali porta il progetto? (Es: riduzione traffico, sicurezza, miglioramento qualità della vita)",
    "benefici_economici": "🔹 Quali vantaggi economici porta il progetto? (Es: risparmio energetico, aumento turismo, creazione posti di lavoro)",
    "nome": "🔹 Qual è il nome del progetto o un termine chiave che lo descrive? (Es: Green City, Progetto LED)",
    "sostenibilita": "🔹 Quali aspetti di sostenibilità sono presenti? (Es: materiali riciclati, pannelli solari, gestione acque)",
    "citta": "🔹 In quale città si trova o si vuole realizzare il progetto?",
    "paese": "🔹 In quale paese si trova o si vuole realizzare il progetto?"
}

def carica_progetti():
    """ Carica i dati dal database SQLite e li restituisce come DataFrame """
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM progetti_successo"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def preprocess_text(text):
    """ Pulisce e normalizza il testo rimuovendo stopwords e caratteri speciali """
    if not isinstance(text, str):
        return ""
    tokens = text.lower().split()
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return " ".join(filtered_tokens)

def estrai_esempi_colonne(df, num_esempi=5):
    """
    Estrai esempi reali dal database per ogni campo.
    """
    esempi = {}
    for col in TEXT_WEIGHTS.keys():
        valori_unici = df[col].dropna().unique()  # Evita valori nulli
        esempi[col] = list(map(str, valori_unici[:num_esempi])) if len(valori_unici) > 0 else []
    return esempi

def chiedi_valore(campo, esempi):
    """ 
    Chiede all'utente di inserire un valore con una spiegazione chiara.
    Se l'utente scrive "Help", mostriamo suggerimenti disponibili.
    Se preme Invio senza scegliere, il parametro viene ignorato.
    """
    while True:
        valore = input(f"\n{DOMANDE[campo]} \n💡 Se vuoi suggerimenti, scrivi 'Help'. Se vuoi lasciare vuoto, premi Invio: ").strip()

        if valore.lower() == "help":
            if esempi:
                print(f"\n🔹 Ecco alcuni esempi disponibili per '{campo}':")
                for i, esempio in enumerate(esempi, start=1):
                    print(f"  {i}. {esempio}")
                valore = input("\n👉 Scegli un'opzione o premi Invio per ignorare: ").strip()
                if valore == "":
                    print(f"⚠ Il campo '{campo}' verrà ignorato.")
                    return ""
                return valore  # Usa il valore scelto
            else:
                print(f"⚠ Nessun esempio disponibile per '{campo}'. Campo ignorato.")
                return ""

        elif valore == "":
            print(f"⚠ Il campo '{campo}' verrà ignorato.")
            return ""

        return valore  # Usa il valore inserito

def crea_testo_pesato_input(df):
    """ 
    Chiede all'utente ogni parametro separatamente con spiegazione chiara, 
    con possibilità di chiedere aiuto e ignorare campi.
    """

    esempi = estrai_esempi_colonne(df)  # Prendiamo esempi reali dal database
    print("\n🔍 Inserisci i dettagli del progetto da confrontare (Premi Invio per saltare un parametro):")

    input_data = {}
    for campo, peso in TEXT_WEIGHTS.items():
        valore = chiedi_valore(campo, esempi[campo])
        input_data[campo] = (valore + " ") * int(peso) if valore else ""

    # Combiniamo i parametri in un'unica stringa
    testo_completo = " ".join(input_data.values())
    return preprocess_text(testo_completo)

def calcola_similarita(df, testo_completo_input):
    """ Calcola la similarità tra il progetto dato e tutti i progetti nel database """

    if df.empty:
        print("❌ Nessun progetto da confrontare!")
        return pd.DataFrame()

    # Carica il vettorizzatore e la matrice TF-IDF salvati
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(MATRIX_PATH, 'rb') as f:
        tfidf_matrix = pickle.load(f)

    # Preprocessiamo l'input dell'utente
    input_vector = vectorizer.transform([testo_completo_input])

    # Calcoliamo la similarità del coseno
    similarita = cosine_similarity(input_vector, tfidf_matrix).flatten()

    # Assegniamo la similarità al DataFrame
    df['similarita'] = similarita

    # Ordiniamo i progetti dal più simile al meno simile
    df_ordinato = df.sort_values(by='similarita', ascending=False)

    return df_ordinato[['id', 'nome', 'citta', 'paese', 'superficie_mq', 'costo_milioni', 'similarita']]




# 📌 Esecuzione principale
if __name__ == "__main__":
    print("📌 Caricamento dei progetti dal database...")
    df = carica_progetti()

    if df.empty:
        print("❌ ERRORE: Il database non contiene progetti!")
    else:
        print("✅ Database caricato con successo!")
        print(df.head())

        # Chiediamo all'utente di inserire ciascun parametro separatamente con spiegazioni chiare
        testo_completo_input = crea_testo_pesato_input(df)

        superficie_input = float(input("📏 Inserisci la superficie del progetto (mq): "))
        costo_input = float(input("💰 Inserisci il costo del progetto (milioni): "))

        print("\n🔍 Calcolo della similarità in corso...")
        df_ordinato = calcola_similarita(df, testo_completo_input)

        superficie_range = (superficie_input * 0.5, superficie_input * 1.5)
        costo_range = (costo_input * 0.5, costo_input * 1.5)


        df_filtrato = df_ordinato[
            (df_ordinato['superficie_mq'].between(*superficie_range)) &
            (df_ordinato['costo_milioni'].between(*costo_range))
        ]

        print("\n📊 Top 5 progetti più simili prima del filtro su superficie/costo:")
        print(df_ordinato[['id', 'nome', 'similarita']].head(5))

        if df_filtrato.empty:
            print("\n⚠ Nessun progetto soddisfa il filtro su superficie/costo!")
            print("🔍 Mostriamo comunque i 5 progetti più simili senza il filtro:\n")
            print(df_ordinato[['id', 'nome', 'citta', 'paese', 'superficie_mq', 'costo_milioni', 'similarita']].head(5))
            df_filtrato = df_ordinato.head(5)  # Prendiamo comunque i top 5 progetti

         # 📌 Salviamo i risultati in CSV con tutte le informazioni del database
        df_filtrato.to_csv(CSV_OUTPUT_PATH, index=False, encoding="utf-8")
        print(f"\n✅ Risultati salvati in {CSV_OUTPUT_PATH}")
        
        print("\n📌 Progetti più simili trovati dopo il filtro su superficie/costo:")
        print(df_filtrato.head())

