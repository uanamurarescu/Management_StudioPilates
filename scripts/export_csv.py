import csv
from pathlib import Path
from app.db import get_connection
ALLOWED_TABLES = {"Clienti", "Antrenori", "Sesiuni",
                  "userC", "Abonamente", "Plati", "Programari",
                  "Review", "Echipamente", "user_log"}
def export_table(table:str, out_Dir: Path = Path("exports")):
    table = table.strip()
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Tabel invalid. Alege din: {sorted(ALLOWED_TABLES)}")
    out_Dir.mkdir(parents=True, exist_ok=True)
    out_path = out_Dir / f"{table}.csv"
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM {table};")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        with out_path.open(mode="w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        print(f"EXPORT OK -> {out_path} (rows={len(rows)})")
    finally:
        cur.close()
        conn.close()
if __name__ == "__main__":
    table = input(f"Tabel ({', '.join(ALLOWED_TABLES)}): ").strip()
    export_table(table)