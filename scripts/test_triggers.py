from app.db import run_execute, run_select

print("TEST TRIGGER BEFORE INSERT (Abonamente)")
try:
    client_id = run_select("SELECT ID_client FROM Clienti LIMIT 1;")[0][0]
    user_id = run_select("SELECT ID_user FROM userC LIMIT 1;")[0][0]
    sesiune_id = run_select("SELECT ID_sesiune FROM Sesiuni LIMIT 1;")[0][0]
except IndexError:
    print("Eroare de accesare date din tabele")
try:
    "INSERT INTO Abonamente (Pret, Durata, Activ, fk_idClientA, fk_idSesiuneA, fk_idUser) VALUES (%s, %s, %s, %s, %s, %s);",
    (100, "1 Luna", "DA", client_id, sesiune_id, user_id)
    print("OK: Inserare valida")
except Exception as e:
    print("EROARE:", e)
print("Inserare invalida")
try:
    run_execute(
        "INSERT INTO Abonamente (Pret, Durata, Activ, fk_idClientA, fk_idSesiuneA, fk_idUser) VALUES (%s, %s, %s, %s, %s, %s);",
        (100, "1 Luna", "Nj", client_id, sesiune_id, user_id)
    )
    print("EROARE: Inserare invalida, trigger NEfunctional")
except Exception as e:
    print("OK: Inserare invalida, RESPINSA DE TRIGGER")
    print("Mesaj DB:", e)

print("\nTEST TRIGGER AFTER UPDATE (Review)")
id_antrenor = run_select("SELECT ID_antrenor, Scor_feedback FROM Antrenori LIMIT 1;")[0]
print(f"Scor actual antrenor (ID {id_antrenor[0]}): {id_antrenor[1]}")
print("Facem update pe scor antrenor (review de nota 5/5)")
run_execute(
    "INSERT INTO Review (Nota_antrenor, Comentariu, fk_idClientR, fk_idAntrenorR) VALUES (%s, %s, %s, %s);",
    (5, "Excelent!", client_id, id_antrenor[0])
)
nou_scor = run_select(f"SELECT Scor_feedback FROM Antrenori WHERE ID_antrenor = {id_antrenor[0]};")[0][0]
print(f"Scor NOU antrenor după trigger: {nou_scor}")

print("\nTEST TRIGGER FINALIZAT")