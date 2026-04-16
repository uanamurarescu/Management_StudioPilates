from pathlib import Path
from app.db import get_connection

def create_tables():
    project_root = Path(__file__).resolve().parent.parent

    conn = get_connection()
    cur = conn.cursor()

    try:
        schema_path = project_root / "sql" / "schema.sql"
        sql_text = schema_path.read_text(encoding="utf-8")
        statements = [s.strip() for s in sql_text.split(";") if s.strip()]
        for stmt in statements:
            cur.execute(stmt)
        print("OK: Tabelele au fost create cu succes!")
        triggers_path = project_root / "sql" / "triggers.sql"
        triggers_text = triggers_path.read_text(encoding="utf-8")
        trigger_blocks = [
            b.strip()
            for b in triggers_text.split("--TRIGGER_END")
            if b.strip()
        ]
        for block in trigger_blocks:
            cur.execute(block)
        print("OK: Triggerele au fost create cu succes!")
        procedures_path = project_root / "sql" / "procedures.sql"
        procedures_text = procedures_path.read_text(encoding="utf-8")
        proc_blocks = [b.strip() for b in procedures_text.split("-- PROC_END") if b.strip()]
        for block in proc_blocks:
            cur.execute(block)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Eroare la crearea tabelelor: ", e)
        raise
    finally:
        cur.close()
        conn.close()
