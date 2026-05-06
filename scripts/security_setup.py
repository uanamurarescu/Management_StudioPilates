import mariadb
import bcrypt
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
ROOT_USER = os.getenv("DB_USER")
ROOT_PASS = os.getenv("DB_PASS")

def get_root_connection():
    return mariadb.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=ROOT_USER,
        password=ROOT_PASS,
        database=DB_NAME
    )

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(
        plain.encode(),
        bcrypt.gensalt()
    ).decode()

def create_db_users():
    conn = get_root_connection()
    cur = conn.cursor()
    manager_pass = os.getenv("MANAGER_PASSWORD")
    comanager_pass = os.getenv("COMANAGER_PASSWORD")
    antrenor_pass = os.getenv("ANTRENOR_PASSWORD")
    client_pass = os.getenv("CLIENT_PASSWORD")
    db_users = [
        ("manager", manager_pass, "ALL PRIVILEGES"),
        ("co-manager", comanager_pass, "SELECT, INSERT, UPDATE, DELETE"),
        ("antrenor", antrenor_pass, "SELECT, UPDATE"),
        ("client", client_pass, "SELECT")
    ]
    for username, password, privileges in db_users:
        try:
            cur.execute(f"DROP USER IF EXISTS '{username}'@'%'")
            cur.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
            cur.execute(f"GRANT {privileges} ON {DB_NAME}.* TO '{username}'@'%'")
            print(f"[OK] Created DB user: {username}")
        except Exception as e:
            print("Error:", e)
    cur.execute("FLUSH PRIVILEGES")
    conn.commit()
    conn.close()

def encrypt_app_users():
    conn = get_root_connection()
    cur = conn.cursor()
    cur.execute("SELECT ID_user, password FROM userC")
    rows = cur.fetchall()
    for row in rows:
        id = row[0]
        pwd = row[1]
        if pwd and not str(pwd).startswith("$2b$"):
            hashed = hash_password(pwd)
            cur.execute(
                "UPDATE userC SET password=? WHERE ID_user=?",
                (hashed, id)
            )
            print(f"[UPDATED] user_id {id} password encrypted")
    conn.commit()
    conn.close()

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("[INFO] NEW KEY GENERATED FOR secret.key")
def load_key():
    return open("secret.key", "rb").read()


def encrypt_sensitive_data():
    key = load_key()
    f = Fernet(key)
    conn = get_root_connection()
    cur = conn.cursor()
    print("[UPDATE] FERNET encrypting table Clients..")
    cur.execute("SELECT ID_client, CNP, Nume, Varsta FROM Clienti")
    rows = cur.fetchall()
    for idC, cnp, nume, varsta in rows:
        updates = []
        params = []
        if cnp and not str(cnp).startswith("gAAAA"):
            updates.append("CNP = %s")
            params.append(f.encrypt(str(cnp).encode()).decode())
        if nume and not str(nume).startswith("gAAAA"):
            updates.append("Nume = %s")
            params.append(f.encrypt(str(nume).encode()).decode())
        if varsta and not str(varsta).startswith("gAAAA"):
            updates.append("Varsta = %s")
            params.append(f.encrypt(str(varsta).encode()).decode())
        if updates:
            sql = f"UPDATE Clienti SET {', '.join(updates)} WHERE ID_client = %s"
            params.append(idC)
            cur.execute(sql, tuple(params))

    print("[UPDATE] FERNET encrypting table userC..")
    cur.execute("SELECT ID_user, username FROM userC")
    users = cur.fetchall()
    for idU, Username in users:
        if Username and not str(Username).startswith("gAAAA"):
            enc_Username = f.encrypt(str(Username).encode()).decode()
            cur.execute("UPDATE userC SET username = %s WHERE ID_user = %s", (enc_Username, idU))
    conn.commit()
    conn.close()

def main():
    print("\n=== CREATE DB USERS + GRANT ===")
    create_db_users()
    print("\n=== ENCRYPT APP USERS PASSWORDS ===")
    encrypt_app_users()
    print("\n SECURITY SETUP COMPLETED")
    generate_key()
    encrypt_sensitive_data()
    print("\n PERSONAL DATA ENCRYPTED USING FERNET")

if __name__ == "__main__":
    main()