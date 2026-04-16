import json
from app.db import get_connection, run_select
print("BOOKING SERVICE")
user_data = run_select("""
    SELECT c.ID_client, u.ID_user 
    FROM Clienti c 
    JOIN userC u ON c.ID_client = u.fk_idClient 
    LIMIT 1
""")
if not user_data:
    print("Eroare: Nu exista clienti cu acest cont de utilizator.")
    exit()
client_id, user_id = user_data[0]
sessions = [
    {"id_s": 1, "st": "confirmata"},
    {"id_s": 2, "st": "in asteptare"},
    {"id_s": 3, "st": "in asteptare"}
]
sessions_json = json.dumps(sessions)
print(f"Apelam procedura booking_session pentru Client ID: {client_id}...")
conn = get_connection()
cur = conn.cursor()
try:
    cur.execute("CALL booking_session(%s, %s, %s, %s, %s);",
                (client_id, user_id, 250, "1 luna", sessions_json))
    row = cur.fetchone()
    id_abonament = row[0]
    while cur.nextset():
        if cur.description is not None:
            cur.fetchall()
    conn.commit()
    print(f"OK: Abonament creat. order_id = {id_abonament}")
finally:
    cur.close()
    conn.close()
print("\nVerificare in DB (abonamente si programari):")
rows = run_select("""
    SELECT a.ID_abonament, p.fk_idSesiunePr, s.Tip_pilates, p.Status_confirmare
    FROM Abonamente a
    JOIN Programari p ON a.fk_idClientA = p.fk_idClientPr
    JOIN Sesiuni s ON p.fk_idSesiunePr = s.ID_sesiune
    WHERE a.ID_abonament = %s
    ORDER BY p.fk_idSesiunePr
""", (id_abonament,))
for r in rows:
    print(r)