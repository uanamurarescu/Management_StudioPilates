import os
import mariadb
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn = mariadb.connect(
        host = os.getenv("DB_HOST", "127.0.0.1"),
        port = int(os.getenv("DB_PORT", "3306")),
        user = os.getenv("DB_USER", "root"),
        password = os.getenv("DB_PASSWORD", "rootpass"),
        database = os.getenv("DB_NAME", "studioPilates_system"),
    )
    return conn

def run_select(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def run_execute(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    return affected

