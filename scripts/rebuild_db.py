from app.db import run_execute
from scripts.create_tables import create_tables

print("Stergem tabelele existente(daca exista)")

run_execute("DROP TABLE IF EXISTS client_log;")
run_execute("DROP TABLE IF EXISTS user_log;")

run_execute("DROP TABLE IF EXISTS Plati;")       # depinde de Abonamente, Clienti
run_execute("DROP TABLE IF EXISTS Programari;")  # depinde de Clienti, Sesiuni
run_execute("DROP TABLE IF EXISTS Review;")      # depinde de Clienti, Antrenori
run_execute("DROP TABLE IF EXISTS Echipamente;") # depinde de Sesiuni, Antrenori

run_execute("DROP TABLE IF EXISTS Abonamente;")  # depinde de Clienti, Sesiuni, userC
run_execute("DROP TABLE IF EXISTS userC;")       # depinde de Clienti
run_execute("DROP TABLE IF EXISTS Sesiuni;")     # depinde de Antrenori

run_execute("DROP TABLE IF EXISTS Clienti;")
run_execute("DROP TABLE IF EXISTS Antrenori;")

print("Creez tabelele din schema sql...")
create_tables()

print("Rebuild gata!")

