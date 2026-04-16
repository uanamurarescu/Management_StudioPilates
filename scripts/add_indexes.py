import time
from app.db import run_execute
def apply_indexes():
    print("=== APLICARE INDEX PENTRU OPTIMIZARE ===")
    drop_queries = [
        "DROP INDEX IF EXISTS idx_users_username ON userC;",
        "DROP INDEX IF EXISTS idx_reviews_nota ON Review;",
        "DROP INDEX IF EXISTS idx_users_actions ON user_log;",
        "DROP INDEX IF EXISTS idx_programari_data ON Programari;",
        "DROP INDEX IF EXISTS idx_clienti_CNP ON Clienti;",
        "DROP INDEX IF EXISTS idx_antrenor_scor ON Antrenori;",
        "DROP INDEX IF EXISTS idx_antrenor_tip_antrenamente ON Antrenori;",
        "DROP INDEX IF EXISTS idx_sesiune_tip_pilates ON Sesiuni;",
        "DROP INDEX IF EXISTS idx_abonamente_status ON Abonamente;"
    ]
    print("Stergere indexi anteriori...")
    for query in drop_queries:
        try:
            run_execute(query)
        except Exception:
            pass
    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_users_username ON userC(username);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_nota ON Review(Nota_antrenor);",
        "CREATE INDEX IF NOT EXISTS idx_users_actions ON user_log(action);",
        "CREATE INDEX IF NOT EXISTS idx_programari_data ON Programari(Data_si_ora);",
        "CREATE INDEX IF NOT EXISTS idx_clienti_CNP ON Clienti(CNP);",
        "CREATE INDEX IF NOT EXISTS idx_antrenor_scor ON Antrenori(Scor_feedback);",
        "CREATE INDEX IF NOT EXISTS idx_antrenor_tip_antrenamente ON Antrenori(Tip_antrenamente);",
        "CREATE INDEX IF NOT EXISTS idx_sesiune_tip_pilates ON Sesiuni(Tip_pilates);",
        "CREATE INDEX IF NOT EXISTS idx_abonamente_status ON Abonamente(Activ);"
    ]
    for query in index_queries:
        print(f"Rulam: {query}")
        try:
            start_time = time.time()
            run_execute(query)
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # ms
            print(f"-> Succes! (Durata creare: {duration:.2f} ms)\n")
        except Exception as e:
            print(f"-> Eroare la crearea indexului: {e}\n")
    print("Indexuri aplicate cu succes.")
    print("---------------------------------------------")
if __name__ == "__main__":
    apply_indexes()