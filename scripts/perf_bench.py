import time
import statistics
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from app.db import run_select, run_execute

RUNS = 30
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
CHART_FILE = OUTPUT_DIR / "performance_chart_extended.png"

def get_test_queries():
    queries = []
    try:
        targets = [
            ("userC", "username", "User: Username"),
            ("Review", "Nota_antrenor", "Review: Nota"),
            ("user_log", "action", "Logs: Action"),
            ("Programari", "Data_si_ora", "Progr: Data"),
            ("Clienti", "CNP", "Client: CNP"),
            ("Antrenori", "Scor_feedback", "Antr: Scor"),
            ("Antrenori", "Tip_antrenamente", "Antr: Tip"),
            ("Sesiuni", "Tip_pilates", "Sesiune: Pilates"),
            ("Abonamente", "Activ", "Abonament: Status")
        ]
        for table, col, label in targets:
            val = run_select(f"SELECT {col} FROM {table} LIMIT 1;")
            if val:
                queries.append({
                    "name": label,
                    "sql": f"SELECT * FROM {table} WHERE {col} = %s;",
                    "params": (val[0][0],)
                })
        return queries
    except Exception as e:
        print(f"Eroare la preluarea datelor: {e}")
        return []

DROP_SQL = [
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

CREATE_SQL = [
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

def run_benchmark(queries, label):
    print(f"Rulăm suita: {label}...")
    results = {}
    for q in queries:
        times = []
        for _ in range(RUNS):
            start = time.perf_counter()
            run_select(q["sql"], q["params"])
            times.append((time.perf_counter() - start) * 1000)
        results[q["name"]] = statistics.mean(times)
        print(f"  {q['name']}: {results[q['name']]:.2f} ms")
    return results

def generate_chart(before, after):
    labels = list(before.keys())
    before_vals = [before[l] for l in labels]
    after_vals = [after[l] for l in labels]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))
    rects1 = ax.bar(x - width/2, before_vals, width, label='Fara Index', color='#e74c3c', alpha=0.8)
    rects2 = ax.bar(x + width/2, after_vals, width, label='Cu Index', color='#2ecc71', alpha=0.8)

    ax.set_ylabel('Timp mediu (ms)')
    ax.set_title(f'Impactul Indexarii asupra Performantei Query-urilor')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    ax.bar_label(rects1, padding=3, fmt='%.2f', fontsize=8)
    ax.bar_label(rects2, padding=3, fmt='%.2f', fontsize=8)

    fig.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"\nGrafic generat: {CHART_FILE}")
    plt.show()

def main():
    test_queries = get_test_queries()
    if not test_queries:
        print("Nu s-au putut genera query-uri de test!")
        return
    print("Stergem indexii pentru testul initial...")
    for sql in DROP_SQL: run_execute(sql)
    before_results = run_benchmark(test_queries, "BEFORE")

    print("\nAplicam indexii...")
    for sql in CREATE_SQL: run_execute(sql)

    print("\nRulam testele după optimizare...")
    after_results = run_benchmark(test_queries, "AFTER")

    generate_chart(before_results, after_results)
if __name__ == "__main__":
    main()