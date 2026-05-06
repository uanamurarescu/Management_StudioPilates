import random
from faker import Faker
from app.db import run_execute, run_select
import os
from dotenv import load_dotenv
load_dotenv()

fake = Faker()

NUM_CLIENTS = 1000
NUM_TRAINERS = 50
NUM_SESSIONS_PER_WEEK = 250
NUM_SUBSCRIPTIONS = 2000
NUM_PAYMENTS = 3000
NUM_BOOKINGS = 2500
NUM_REVIEWS = 1000
NUM_MACHINES = 400
NUM_USERS = 3000
NUM_USERS_LOG = 4000
admin_pass = os.getenv("ADMIN_PASS")

print("Cream user admin fix")
run_execute(
    "INSERT IGNORE INTO userC (username, password) VALUES (%s, %s);",
    ("admin", admin_pass)
)

print("Generam clienti...")
for _ in range(NUM_CLIENTS):
    run_execute("""
        INSERT INTO Clienti (CNP, Nume, Prenume, Varsta, Nivel_sedentarism, Sesiune_dorita)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        fake.unique.random_number(digits=13),
        fake.last_name(),
        fake.first_name(),
        random.randint(18, 65),
        random.choice(["scazut", "mediu", "ridicat"]),
        random.choice(["pilates pe saltea", "reformer pilates", "cadillac pilates", "pilates aparate auxiliare",
                       "pilates flow" ,"pilates terapeutic", "pilates pentru sportivi", "pilates pre-natal",
                       "pilates post-natal", "winsor pilates"])
    ))


print("Generam useri cu parole simple pentru clienti...")
simple_passwords = [
    "pass8976",
    "parola121",
    "parara89",
    "qwerty2026",
    "sportiv67",
    "parolAA",
    "pilaTES89",
    "pwpwpw",
    "1234pilates2026",
    "student9089",
    "stud78"
]

clienti_full = run_select("SELECT ID_client, Nume, Prenume FROM Clienti")

for client in clienti_full:
    client_id, nume, prenume = client
    suffix = fake.unique.bothify(text='#####')
    username = f"{prenume.lower()}.{nume.lower()[:10]}{suffix}"
    password = random.choice(simple_passwords)

    run_execute("""
        INSERT INTO userC (username, password, fk_idClient)
        VALUES (%s, %s, %s)
    """, (
        username,
        password,
        client_id
    ))


print("Generam antrenori...")
for _ in range(NUM_TRAINERS):
    run_execute("""
        INSERT INTO Antrenori (Nume, Prenume, Nivel_antrenamente, Tip_antrenamente, Scor_feedback)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        fake.last_name(),
        fake.first_name(),
        random.choice(["incepator", "mediu", "avansat"]),
        random.choice(["pilates pe saltea", "reformer pilates", "cadillac pilates", "pilates aparate auxiliare",
                       "pilates flow" ,"pilates terapeutic", "pilates pentru sportivi", "pilates pre-natal",
                       "pilates post-natal", "winsor pilates"]),
        random.randint(1, 5)
    ))

print("Generam sesiuni saptamanale...")
antrenori = run_select("SELECT ID_antrenor FROM Antrenori")
for _ in range(NUM_SESSIONS_PER_WEEK):
    run_execute("""
        INSERT INTO Sesiuni (Tip_pilates, Tip_sesiune, Capacitate_maxima, Nivel_dificultate, Durata, Data_si_ora, fk_idAntrenorS)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        random.choice(["pilates pe saltea", "reformer pilates", "cadillac pilates", "pilates aparate auxiliare",
                       "pilates flow" ,"pilates terapeutic", "pilates pentru sportivi", "pilates pre-natal",
                       "pilates post-natal", "winsor pilates"]),
        random.choice(["grup", "individual"]),
        random.randint(5, 20),
        random.choice(["usor", "mediu", "greu"]),
        f"{random.randint(30,90)} min",
        fake.date_time_this_year(),
        random.choice(antrenori)[0]
    ))

print("Generam abonamente...")
clienti = run_select("SELECT ID_client FROM Clienti")
sesiuni = run_select("SELECT ID_sesiune FROM Sesiuni")
userID = run_select("SELECT ID_user FROM userC")
for _ in range(NUM_SUBSCRIPTIONS):
    run_execute("""
        INSERT INTO Abonamente (Pret, Durata, Activ, fk_idClientA, fk_idSesiuneA, fk_idUser)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        random.randint(100, 500),
        random.choice(["1 luna", "3 luni", "6 luni", "12 luni"]),
        random.choice(["DA", "NU"]),
        random.choice(clienti)[0],
        random.choice(sesiuni)[0],
        random.choice(userID)[0]
    ))

print("Generam plati...")
abonamente = run_select("SELECT ID_abonament, fk_idClientA FROM Abonamente")
for abon in abonamente:
    run_execute("""
        INSERT INTO Plati (fk_idClientP, fk_idAbonamentP)
        VALUES (%s, %s)
    """, (abon[1], abon[0]))

print("Generam programari...")
for _ in range(NUM_BOOKINGS):
    run_execute("""
        INSERT INTO Programari (Data_si_ora, Status_confirmare, fk_idClientPr, fk_idSesiunePr)
        VALUES (%s, %s, %s, %s)
    """, (
        fake.date_time_this_year(),
        random.choice(["confirmata", "in asteptare"]),
        random.choice(clienti)[0],
        random.choice(sesiuni)[0]
    ))

print("Generam review-uri...")
for _ in range(NUM_REVIEWS):
    comentariu_limitat = fake.text(max_nb_chars=400)
    run_execute("""
        INSERT INTO Review (Comentariu, Nota_antrenor, fk_idClientR, fk_idAntrenorR)
        VALUES (%s, %s, %s, %s)
    """, (
        comentariu_limitat,
        random.randint(1, 5),
        random.choice(clienti)[0],
        random.choice(antrenori)[0]
    ))

print("Generam echipamente...")
for _ in range(NUM_MACHINES):
    run_execute("""
        INSERT INTO Echipamente (Denumire, Stare_echipament, Data_verificare_echipament, fk_idSesiuneE, fk_idAntrenorE)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        random.choice(["Reformer", "Saltea", "Cadillac", "Minge", "Banda"]),
        random.choice(["conform", "nou", "uzat" , "defect"]),
        fake.date_time_this_year(),
        random.choice(sesiuni)[0],
        random.choice(antrenori)[0]
    ))


#user log si user action
print("Generam user_log...")
actions = [
    "login",
    "logout",
    "programare_creata",
    "programare_anulata",
    "feedback_adaugat",
    "abonament_cumparat",
    "abonament_anulat",
    "plata_efectuata",
    "refund_plata"
]

print("Initializam user_action avansat...")

users = run_select("SELECT ID_user FROM userC")
user_action = {}

for (user_id,) in users:
    user_action[user_id] = {
        "logged_in": False,
        "programari_active": 0,
        "abonament_activ": random.choice([True, False]),
        "programari_anulate": 0,
        "plati_efectuate": 0,
        "feedback_adaugat": 0,
        "refund_plata": 0
    }

print("Generam user_log realist...")

for _ in range(NUM_USERS_LOG):
    user_id = random.choice(list(user_action.keys()))
    state = user_action[user_id]

    possible_actions = []

    if not state["logged_in"]:
        possible_actions.append("login")
    else:
        possible_actions.append("logout")
        possible_actions.append("programare_creata")

        if state["programari_active"] > 0:
            possible_actions.append("programare_anulata")
            possible_actions.append("feedback_adaugat")

        if not state["abonament_activ"]:
            possible_actions.append("abonament_cumparat")
        else:
            possible_actions.append("plata_efectuata")
            possible_actions.append("abonament_anulat")

        if state["plati_efectuate"] > 0:
            possible_actions.append("refund_plata")

    action = random.choice(possible_actions)

    if action == "login":
        state["logged_in"] = True
    elif action == "logout":
        state["logged_in"] = False
    elif action == "programare_creata":
        state["programari_active"] += 1
    elif action == "programare_anulata":
        if state["programari_active"] > 0:
            state["programari_active"] -= 1
        state["programari_anulate"] += 1
    elif action == "feedback_adaugat":
        state["feedback_adaugat"] += 1
    elif action == "abonament_cumparat":
        state["abonament_activ"] = True
        state["plati_efectuate"] += 1
    elif action == "abonament_anulat":
        state["abonament_activ"] = False
        if state["plati_efectuate"] > 0:
            state["plati_efectuate"] -= 1
        state["refund_plata"] += 1
    elif action == "plata_efectuata":
        state["plati_efectuate"] += 1
    elif action == "refund_plata":
        state["refund_plata"] += 1
        state["plati_efectuate"] -= 1

    run_execute("""
        INSERT INTO user_log (user_id, action)
        VALUES (%s, %s)
    """, (user_id, action))

print("Date generate corect!")
