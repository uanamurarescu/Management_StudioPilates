import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from app.db import run_select, run_execute

app = Flask(__name__)
app.secret_key = "dev-secret"

CRUD_CONFIG = {
    "Clienti": {
        "pk": "ID_client",
        "title": "Clienti",
        "create_fields": ["CNP", "Nume", "Prenume", "Varsta", "Nivel_sedentarism", "Sesiune_dorita"],
        "update_fields": ["Nume", "Prenume", "Varsta", "Nivel_sedentarism", "Sesiune_dorita"],
        "list_fields": ["ID_client", "Nume", "Prenume", "CNP"],
        "default_sort": "ID_client DESC",
        "children": [
            {"table": "userC", "fk": "fk_idClient"},
            {"table": "Abonamente", "fk": "fk_idClientA"},
            {"table": "Programari", "fk": "fk_idClientPr"},
        ],
    },
    "Antrenori": {
        "pk": "ID_antrenor",
        "title": "Antrenori",
        "create_fields": ["Nume", "Prenume", "Nivel_antrenamente", "Tip_antrenamente", "Scor_feedback"],
        "update_fields": ["Nivel_antrenamente", "Tip_antrenamente", "Scor_feedback"],
        "list_fields": ["ID_antrenor", "Nume", "Prenume", "Tip_antrenamente"],
        "default_sort": "ID_antrenor DESC",
        "children": [
            {"table": "Sesiuni", "fk": "fk_idAntrenorS"},
            {"table": "Review", "fk": "fk_idAntrenorR"},
        ],
    },
    "Sesiuni": {
        "pk": "ID_sesiune",
        "title": "Sesiuni Pilates",
        "create_fields": ["Tip_pilates", "Tip_sesiune", "Capacitate_maxima", "Nivel_dificultate", "Durata",
                          "Data_si_ora", "fk_idAntrenorS"],
        "update_fields": ["Capacitate_maxima", "Nivel_dificultate", "Durata"],
        "list_fields": ["ID_sesiune", "Tip_pilates", "Data_si_ora", "fk_idAntrenorS"],
        "default_sort": "Data_si_ora DESC",
        "fk_dropdowns": {"fk_idAntrenorS": ("Antrenori", "ID_antrenor", "Nume")},
    },
    "userC": {
        "pk": "ID_user",
        "title": "Conturi Utilizatori",
        "create_fields": ["username", "password", "fk_idClient"],
        "update_fields": ["password"],
        "list_fields": ["ID_user", "username", "fk_idClient"],
        "default_sort": "ID_user DESC",
        "fk_dropdowns": {"fk_idClient": ("Clienti", "ID_client", "Nume")},
    },
    "Abonamente": {
        "pk": "ID_abonament",
        "title": "Abonamente",
        "create_fields": ["Pret", "Durata", "Activ", "fk_idClientA", "fk_idSesiuneA", "fk_idUser"],
        "update_fields": ["Activ"],
        "list_fields": ["ID_abonament", "Pret", "Activ", "fk_idClientA"],
        "default_sort": "ID_abonament DESC",
        "fk_dropdowns": {
            "fk_idClientA": ("Clienti", "ID_client", "Nume"),
            "fk_idSesiuneA": ("Sesiuni", "ID_sesiune", "Tip_pilates"),
            "fk_idUser": ("userC", "ID_user", "username")
        },
    },
    "Plati": {
        "pk": "ID_plata",
        "title": "Plati",
        "create_fields": ["fk_idClientP", "fk_idAbonamentP"],
        "update_fields": [],
        "list_fields": ["ID_plata", "Data_si_ora", "fk_idClientP", "fk_idAbonamentP"],
        "default_sort": "Data_si_ora DESC",
        "fk_dropdowns": {
            "fk_idClientP": ("Clienti", "ID_client", "Nume"),
            "fk_idAbonamentP": ("Abonamente", "ID_abonament", "ID_abonament")
        },
    },
    "Programari": {
        "pk": "ID_programare",
        "title": "Programari",
        "create_fields": ["Data_si_ora", "Status_confirmare", "fk_idClientPr", "fk_idSesiunePr"],
        "update_fields": ["Status_confirmare"],
        "list_fields": ["ID_programare", "Data_si_ora", "Status_confirmare"],
        "default_sort": "Data_si_ora DESC",
        "fk_dropdowns": {
            "fk_idClientPr": ("Clienti", "ID_client", "Nume"),
            "fk_idSesiunePr": ("Sesiuni", "ID_sesiune", "Tip_pilates")
        },
    },
}


# --- FUNCTII HELPER ---

def ensure_table_allowed(table):
    if table not in CRUD_CONFIG:
        abort(404)
    return CRUD_CONFIG[table]


def has_any_user():
    try:
        # Verificăm în tabelul tău userC
        rows = run_select("SELECT ID_user FROM userC LIMIT 1;")
        return bool(rows)
    except Exception:
        return False


def record_exists(table, field, value):
    ensure_table_allowed(table)
    q = f"SELECT 1 FROM {table} WHERE {field}=%s LIMIT 1;"
    return bool(run_select(q, (value,)))


def fetch_list(table):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} ORDER BY {cfg.get('default_sort', pk + ' DESC')};"
    rows = run_select(q)
    return cols, rows


def fetch_by_id(table, rec_id):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} WHERE {pk}=%s LIMIT 1;"
    rows = run_select(q, (rec_id,))
    return cols, (rows[0] if rows else None)


def build_fk_options(cfg):
    options = {}
    for field, spec in cfg.get("fk_dropdowns", {}).items():
        parent_table, parent_pk, label_col = spec
        rows = run_select(
            f"SELECT {parent_pk}, {label_col} FROM {parent_table} ORDER BY {parent_pk} DESC;"
        )
        options[field] = [(str(r[0]), str(r[1])) for r in rows]
    return options


def insert_record(table, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["create_fields"]
    values = []

    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Camp obligatoriu lipsa: {f}")
        values.append(v)

    for f, v in zip(fields, values):
        if f.endswith("_id") and "fk_dropdowns" in cfg and f in cfg["fk_dropdowns"]:
            parent_table, parent_pk, _label = cfg["fk_dropdowns"][f]
            if not record_exists(parent_table, parent_pk, v):
                raise ValueError(f"Valoare invalida pentru {f} (nu exista in {parent_table}).")

    cols = ", ".join(fields)
    placeholders = ", ".join(["%s"] * len(fields))
    q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders});"
    run_execute(q, tuple(values))


def update_record(table, rec_id, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["update_fields"]
    if not fields:
        raise ValueError("Update nepermis pentru acest tabel.")

    pairs = []
    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Camp obligatoriu lipsa: {f}")
        pairs.append(f"{f}=%s")
        values.append(v)

    values.append(rec_id)

    q = f"UPDATE {table} SET {', '.join(pairs)} WHERE {cfg['pk']}=%s;"
    run_execute(q, tuple(values))


def delete_record_safe(table, rec_id):
    cfg = ensure_table_allowed(table)

    for ch in cfg.get("children", []):
        run_execute(f"DELETE FROM {ch['table']} WHERE {ch['fk']}=%s;", (rec_id,))
    run_execute(f"DELETE FROM {table} WHERE {cfg['pk']}=%s;", (rec_id,))


# --- RUTE FLASK ---
@app.before_request
def guard_if_no_users():
    allowed = {"/", "/setup", "/seed-admin", "/search"}
    if request.path.startswith("/static/"):
        return
    if not has_any_user() and request.path not in allowed:
        return redirect(url_for("setup_required"))

@app.route("/")
def index():
    counts = {}
    ready = has_any_user()
    for t in CRUD_CONFIG.keys():
        try:
            counts[t] = run_select(f"SELECT COUNT(*) FROM {t};")[0][0] if ready else 0
        except Exception:
            counts[t] = 0
    return render_template("index.html", site_cfg=CRUD_CONFIG, counts=counts, ready=ready)

@app.route("/setup")
def setup_required():
    return render_template("setup_required.html", site_cfg=CRUD_CONFIG)

@app.route("/seed-admin")
def seed_admin():
    if has_any_user():
        flash("Exista deja utilizatori in sistem.", "info")
        return redirect(url_for("crud_list", table="userC"))

    # pentru a respecta FK)
    run_execute("INSERT INTO Clienti (CNP, Nume, Prenume, Varsta,  Nivel_sedentarism, Sesiune_dorita) VALUES (%s, %s, %s, %s, %s, %s)",
                ("0000000000000","Sistem", "Admin", "99", "Scazut", "reformer pilates"))
    last_id = run_select("SELECT LAST_INSERT_ID()")[0][0]

    # Cream userul legat de clientul de mai sus
    run_execute("INSERT INTO userC (username, password, fk_idClient) VALUES (%s, %s, %s);",
                ("admin", "admin123", last_id))

    flash("Cont administrator creat cu succes (user: admin / pass: admin123).", "success")
    return redirect(url_for("crud_list", table="userC"))

@app.route("/crud/<table>")
def crud_list(table):
    cfg = ensure_table_allowed(table)
    cols, rows = fetch_list(table)
    return render_template(
        "crud_list.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        cols=cols,
        rows=rows,
    )


@app.route("/crud/<table>/create", methods=["GET", "POST"])
def crud_create(table):
    cfg = ensure_table_allowed(table)
    fk_options = build_fk_options(cfg)
    if request.method == "POST":
        try:
            insert_record(table, request.form)
            flash("Creat cu succes.", "success");
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")
    return render_template("crud_form.html", site_cfg=CRUD_CONFIG, table=table, table_cfg=cfg, mode="create",
                           fields=cfg["create_fields"], fk_options=fk_options, choices=cfg.get("choices", {}),values={},)

@app.route("/crud/<table>/edit/<int:rec_id>", methods=["GET", "POST"])
def crud_edit(table, rec_id):
    cfg = ensure_table_allowed(table)
    cols, row = fetch_by_id(table, rec_id)
    if not row:
        abort(404)

    values = dict(zip(cols, row))
    fk_options = build_fk_options(cfg)

    if request.method == "POST":
        try:
            update_record(table, rec_id, request.form)
            flash("Update reusit.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")

    return render_template(
        "crud_form.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        mode="edit",
        fields=cfg["update_fields"],
        values=values,
        fk_options=fk_options,
        choices=cfg.get("choices", {}),
        rec_id=rec_id,
    )

@app.route("/crud/<table>/delete/<int:rec_id>", methods=["POST"])
def crud_delete(table, rec_id):
    ensure_table_allowed(table)
    try:
        delete_record_safe(table, rec_id)
        flash("Sters cu succes.", "success")
    except Exception as e:
        flash(f"Eroare la stergere: {str(e)}", "error")

    return redirect(url_for("crud_list", table=table))

@app.route("/search", methods=["GET", "POST"])
def search():
    result = None
    if request.method == "POST":
        table = (request.form.get("table") or "").strip()
        field = (request.form.get("field") or "").strip()
        value = (request.form.get("value") or "").strip()
        try:
            ensure_table_allowed(table)
            exists = record_exists(table, field, value)
            result = {"ok": True, "exists": exists, "table": table, "field": field, "value": value}
        except Exception as e:
            result = {"ok": False, "error": str(e)}
    return render_template("search.html", site_cfg=CRUD_CONFIG, result=result)


if __name__ == "__main__":
    app.run(debug=True)