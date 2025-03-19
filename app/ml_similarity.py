# import os
# import pickle
# import sqlite3
# import pandas as pd
# from sklearn.metrics.pairwise import cosine_similarity

# # 📌 Percorsi aggiornati dei file
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(BASE_DIR, "Progetto_DB", "progetti_DB.sqlite")
# VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")
# MATRIX_PATH = os.path.join(BASE_DIR, "tfidf_matrix.pkl")

# def carica_progetti():
#     """ Carica i dati dal database SQLite e li restituisce come DataFrame """
#     conn = sqlite3.connect(DB_PATH)
#     query = "SELECT * FROM progetti_successo"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def calcola_similarita(df, project_input):
#     """ Calcola la similarità tra il progetto dato e tutti i progetti nel database """
#     if df.empty:
#         return pd.DataFrame()

#     # Carica il vettorizzatore e la matrice TF-IDF salvati
#     with open(VECTORIZER_PATH, 'rb') as f:
#         vectorizer = pickle.load(f)
#     with open(MATRIX_PATH, 'rb') as f:
#         tfidf_matrix = pickle.load(f)

#     # Combiniamo i parametri testuali dell'utente in un'unica stringa
#     testo_input = " ".join([
#         project_input.problema,
#         project_input.interventi,
#         project_input.tipologia,
#         project_input.benefici_sociali,
#         project_input.benefici_economici,
#         project_input.nome,
#         project_input.sostenibilita,
#         project_input.citta,
#         project_input.paese
#     ])

#     # Vettorizza l'input dell'utente
#     input_vector = vectorizer.transform([testo_input])

#     # Calcoliamo la similarità del coseno
#     similarita = cosine_similarity(input_vector, tfidf_matrix).flatten()

#     # Aggiungiamo la similarità ai progetti
#     df['similarita'] = similarita

#     # Ordiniamo per similarità
#     df_ordinato = df.sort_values(by='similarita', ascending=False)

#     # Applichiamo i filtri su superficie e costo
#     superficie_range = (project_input.superficie_mq * 0.5, project_input.superficie_mq * 1.5)
#     costo_range = (project_input.costo_milioni * 0.5, project_input.costo_milioni * 1.5)

#     df_filtrato = df_ordinato[
#         (df_ordinato['superficie_mq'].between(*superficie_range)) &
#         (df_ordinato['costo_milioni'].between(*costo_range))
#     ]

#     if df_filtrato.empty:
#         df_filtrato = df_ordinato.head(5)  # Prendiamo comunque i top 5 progetti

#     return df_filtrato[['id', 'nome', 'citta', 'paese', 'superficie_mq', 'costo_milioni', 'similarita']].head(5).to_dict(orient="records")
import os
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 📌 Percorso del database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Progetto_DB", "progetti_DB.sqlite")

def carica_progetti():
    """ Carica i dati dal database SQLite e li restituisce come DataFrame """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM progetti_successo", conn)
    conn.close()
    return df

def calcola_similarita(project_input):
    """ Calcola la similarità tra il progetto dato e tutti i progetti nel database, senza usare pickle. """
    
    # 📌 Carichiamo i progetti aggiornati dal database
    df = carica_progetti()
    
    if df.empty:
        return []

    # 📌 Combiniamo i campi testuali per creare il dataset TF-IDF
    df["testo_completo"] = df[[
        "problema", "interventi", "tipologia", 
        "benefici_sociali", "benefici_economici", 
        "nome", "sostenibilita", "citta", "paese"
    ]].fillna("").agg(" ".join, axis=1)

    # 📌 Creiamo il TF-IDF dinamicamente
    vectorizer = TfidfVectorizer(max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(df["testo_completo"])

    # 📌 Prepara l'input dell'utente per la similarità
    testo_input = " ".join([
        project_input.problema, project_input.interventi, project_input.tipologia,
        project_input.benefici_sociali, project_input.benefici_economici,
        project_input.nome, project_input.sostenibilita, project_input.citta, project_input.paese
    ])

    input_vector = vectorizer.transform([testo_input])

    # 📌 Calcoliamo la similarità del coseno
    similarita = cosine_similarity(input_vector, tfidf_matrix).flatten()

    # 📌 Aggiungiamo la similarità ai progetti
    df['similarita'] = similarita

    # 📌 Ordiniamo i progetti per similarità
    df_ordinato = df.sort_values(by='similarita', ascending=False)

    # 📌 Convertiamo le colonne `superficie_mq` e `costo_milioni` in float
    df_ordinato["superficie_mq"] = pd.to_numeric(df_ordinato["superficie_mq"], errors="coerce")
    df_ordinato["costo_milioni"] = pd.to_numeric(df_ordinato["costo_milioni"], errors="coerce")

    # 📌 Filtriamo i progetti in base alla superficie e al costo
    superficie_range = (project_input.superficie_mq * 0.5, project_input.superficie_mq * 1.5)
    costo_range = (project_input.costo_milioni * 0.5, project_input.costo_milioni * 1.5)

    df_filtrato = df_ordinato[
        (df_ordinato["superficie_mq"].between(*superficie_range)) &
        (df_ordinato["costo_milioni"].between(*costo_range))
    ]

    # 📌 Se il DataFrame filtrato è vuoto, mostriamo comunque i primi 5 progetti più simili
    if df_filtrato.empty:
        df_filtrato = df_ordinato.head(5)

    return df_filtrato[['id', 'nome', 'citta', 'paese', 'superficie_mq', 'costo_milioni', 'similarita']].head(5).to_dict(orient="records")
