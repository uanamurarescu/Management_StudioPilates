import csv
from pathlib import Path
from app.db import get_connection

ALLOWED_TABLES = {
    "Clienti", "Antrenori", "Sesiuni", "userC",
    "Abonamente", "Plati", "Programari", "Review",
    "Echipamente", "user_log"
}

def get_table_info(cur, table: str):
    cur.execute(f"DESCRIBE {table};")
    valid_cols = set()
    dynamic_skip_cols = {"created_at", "Data_si_ora"}
    for row in cur.fetchall():
        col_name = row[0]
        extra = row[5] if len(row) > 5 else ""
        valid_cols.add(col_name)

        if extra and 'auto_increment' in extra.lower():
            dynamic_skip_cols.add(col_name)
    return valid_cols, dynamic_skip_cols

def import_table_from_csv(table: str, csv_path: Path, truncate_first: bool = False):
    table = table.strip()
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Tabel invalid. Alege din: {sorted(ALLOWED_TABLES)}")
    if not csv_path.exists():
        raise FileNotFoundError(f"Nu exista CSV la calea: {csv_path}")
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    skipped = 0

    try:
        table_cols, dynamic_skip_cols = get_table_info(cur, table)
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV invalid: lipseste header-ul.")
            cols = []
            for c in reader.fieldnames:
                c_clean = c.strip()
                if c_clean in dynamic_skip_cols:
                    continue
                if c_clean in table_cols:
                    cols.append(c_clean)
            if not cols:
                raise ValueError("Nu am gasit coloane importabile care sa coincida cu schema DB.")
            placeholders = ",".join(["%s"] * len(cols))
            col_list = ",".join(cols)
            sql = f"INSERT IGNORE INTO {table} ({col_list}) VALUES ({placeholders});"
            conn.begin()
            if truncate_first:
                cur.execute(f"SET FOREIGN_KEY_CHECKS = 0;")
                cur.execute(f"TRUNCATE TABLE {table};")
                cur.execute(f"SET FOREIGN_KEY_CHECKS = 1;")
            for i, row in enumerate(reader, start=2):
                values = []
                empty_row = True
                for c in cols:
                    val = row.get(c)
                    val = val.strip() if val is not None else ""
                    if val != "":
                        empty_row = False
                    values.append(val if val != "" else None)
                if empty_row:
                    skipped += 1
                    continue
                cur.execute(sql, tuple(values))
                inserted += cur.rowcount
            conn.commit()
            print(f"IMPORT OK -> tabel={table}, randuri inserate={inserted}, sarite={skipped}")
    except Exception as e:
        conn.rollback()
        print(f"IMPORT FAIL -> rollback executat. Eroare: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    t_name = input(f"Tabel ({', '.join(sorted(ALLOWED_TABLES))}): ").strip()
    p_str = input("Cale fisier CSV (ex: exports/AntrenoriNoi.csv): ").strip()
    trunc = input("TRUNCATE inainte? (y/n): ").strip().lower() == "y"
    import_table_from_csv(t_name, Path(p_str), truncate_first=trunc)